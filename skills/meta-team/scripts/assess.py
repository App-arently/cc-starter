#!/usr/bin/env python3
"""Decomposability scorer for meta-team task assessment.

Determines whether a prompt should be handled by a single agent or a team,
based on deliverable independence and tool density.

Grounded in: Google arxiv 2512.08296 — decomposability + tool density
predict optimal multi-agent architecture with 87% accuracy.

Usage:
    echo '{"objective":"...","deliverables":[...],"constraints":[],"existing_codebase":false}' | python3 assess.py
"""

import json
import sys
from collections import defaultdict


def compute_file_coupling(deliverables: list[dict]) -> float:
    """Fraction of file references shared between deliverables. 0=fully independent, 1=fully coupled."""
    if len(deliverables) < 2:
        return 0.0

    file_owners = defaultdict(set)
    all_files = set()

    for i, d in enumerate(deliverables):
        for f in d.get("files", []):
            file_owners[f].add(i)
            all_files.add(f)

    if not all_files:
        return 0.0

    shared = sum(1 for f in all_files if len(file_owners[f]) > 1)
    return shared / len(all_files)


def estimate_tool_density(deliverables: list[dict]) -> str:
    """Classify expected tool call density per deliverable."""
    total_tools = sum(len(d.get("tools", [])) for d in deliverables)
    avg = total_tools / max(len(deliverables), 1)

    if avg <= 2:
        return "low"
    elif avg <= 5:
        return "medium"
    else:
        return "high"


def compute_decomposability(deliverables: list[dict], existing_codebase: bool) -> float:
    """Score 0.0-1.0. Higher = more parallelizable = better for team."""
    n = len(deliverables)
    if n < 2:
        return 0.0

    coupling = compute_file_coupling(deliverables)

    # Independence ratio: what fraction of deliverables share no files
    file_owners = defaultdict(set)
    for i, d in enumerate(deliverables):
        for f in d.get("files", []):
            file_owners[f].add(i)

    coupled_deliverables = set()
    for f, owners in file_owners.items():
        if len(owners) > 1:
            coupled_deliverables.update(owners)

    independence = 1.0 - (len(coupled_deliverables) / n)

    # Base score: weighted combination
    score = (independence * 0.6) + ((1.0 - coupling) * 0.3)

    # Bonus for many deliverables (more parallelism opportunity)
    if n >= 4:
        score += 0.1
    elif n >= 3:
        score += 0.05

    # Penalty for existing codebase (more implicit coupling)
    if existing_codebase:
        score -= 0.1

    return max(0.0, min(1.0, round(score, 3)))


def assess(input_data: dict) -> dict:
    deliverables = input_data.get("deliverables", [])
    existing_codebase = input_data.get("existing_codebase", False)

    decomposability = compute_decomposability(deliverables, existing_codebase)
    tool_density = estimate_tool_density(deliverables)

    # Decision threshold from Google 2512.08296
    threshold = 0.45
    if decomposability >= threshold and len(deliverables) >= 2:
        recommendation = "team"
    else:
        recommendation = "single"

    # Build reasoning
    coupling = compute_file_coupling(deliverables)
    parts = [
        f"{len(deliverables)} deliverables",
        f"file coupling={coupling:.2f}",
        f"tool density={tool_density}",
    ]
    if existing_codebase:
        parts.append("existing codebase (-0.1)")
    reasoning = f"Score {decomposability:.3f} ({'above' if decomposability >= threshold else 'below'} {threshold} threshold). {', '.join(parts)}."

    return {
        "decomposability": decomposability,
        "tool_density": tool_density,
        "recommendation": recommendation,
        "reasoning": reasoning,
    }


if __name__ == "__main__":
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON input: {e}"}))
        sys.exit(1)

    result = assess(data)
    print(json.dumps(result, indent=2))
