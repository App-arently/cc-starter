#!/usr/bin/env python3
"""Token budget allocator for meta-team cost estimation.

Estimates per-agent token usage and cost based on task complexity and model tier.
Applies review overhead multiplier from Tokenomics research.

Grounded in: Tokenomics 2601.14470 (59.4% tokens go to review stage),
BAMAS 2511.21572 (ILP budget allocation).

Usage:
    echo '{"tasks":[{"name":"scaffold","complexity":"simple","model_tier":"haiku"}],"budget_limit":5.0}' | python3 budget.py
"""

import json
import sys
from pathlib import Path

import yaml

# Base token estimates per complexity level
BASE_TOKENS = {
    "simple": 5_000,
    "medium": 15_000,
    "complex": 40_000,
}

# Review overhead: Tokenomics 2601.14470 finds 59.4% of tokens go to review
REVIEW_MULTIPLIER = 1.6

# Meta-team orchestrator overhead (opus tokens for planning + judging)
META_OVERHEAD_TOKENS = {"input": 35_000, "output": 10_000}

# Variance for optimistic/pessimistic estimates
OPTIMISTIC_FACTOR = 0.7
PESSIMISTIC_FACTOR = 1.8


def load_pricing() -> dict:
    pricing_path = Path(__file__).parent / "pricing.yaml"
    if pricing_path.exists():
        with open(pricing_path) as f:
            return yaml.safe_load(f)
    # Fallback defaults (March 2026 pricing)
    return {
        "models": {
            "haiku": {"input_per_1m": 0.80, "output_per_1m": 4.00},
            "sonnet": {"input_per_1m": 3.00, "output_per_1m": 15.00},
            "opus": {"input_per_1m": 15.00, "output_per_1m": 75.00},
        }
    }


def estimate_cost(tokens: int, model: str, pricing: dict) -> float:
    """Estimate cost assuming 70/30 input/output split."""
    model_pricing = pricing["models"].get(model, pricing["models"]["sonnet"])
    input_tokens = int(tokens * 0.7)
    output_tokens = int(tokens * 0.3)
    cost = (input_tokens / 1_000_000 * model_pricing["input_per_1m"]) + (
        output_tokens / 1_000_000 * model_pricing["output_per_1m"]
    )
    return round(cost, 4)


def allocate(input_data: dict) -> dict:
    tasks = input_data.get("tasks", [])
    budget_limit = input_data.get("budget_limit")
    pricing = load_pricing()

    per_agent = []
    total_tokens = 0

    for task in tasks:
        name = task.get("name", "unnamed")
        complexity = task.get("complexity", "medium")
        model = task.get("model_tier", "sonnet")

        base = BASE_TOKENS.get(complexity, BASE_TOKENS["medium"])
        with_review = int(base * REVIEW_MULTIPLIER)
        cost = estimate_cost(with_review, model, pricing)

        per_agent.append({
            "name": name,
            "model": model,
            "estimated_tokens": with_review,
            "estimated_cost": cost,
        })
        total_tokens += with_review

    # Meta overhead (always opus)
    meta_cost = estimate_cost(
        META_OVERHEAD_TOKENS["input"] + META_OVERHEAD_TOKENS["output"],
        "opus",
        pricing,
    )

    expected_total = sum(a["estimated_cost"] for a in per_agent) + meta_cost
    optimistic_total = round(expected_total * OPTIMISTIC_FACTOR, 4)
    pessimistic_total = round(expected_total * PESSIMISTIC_FACTOR, 4)

    budget_ok = True
    if budget_limit is not None:
        budget_ok = pessimistic_total <= budget_limit

    return {
        "per_agent": per_agent,
        "total": {
            "optimistic": optimistic_total,
            "expected": round(expected_total, 4),
            "pessimistic": pessimistic_total,
        },
        "meta_overhead": meta_cost,
        "budget_ok": budget_ok,
    }


if __name__ == "__main__":
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON input: {e}"}))
        sys.exit(1)

    result = allocate(data)
    print(json.dumps(result, indent=2))
