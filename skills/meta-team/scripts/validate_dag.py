#!/usr/bin/env python3
"""DAG validator for meta-team task graphs.

Detects cycles via Kahn's BFS topological sort, computes critical path,
generates spawn waves, and warns on excessive depth.

Grounded in: TDAG 2402.10178 (Kahn's spawn ordering), IBM 2511.10650
(unsupervised cycle detection in agentic applications).

Usage:
    echo '[{"id":"t1","deps":[],"agent":"scaffold","complexity":"simple"}, ...]' | python3 validate_dag.py
"""

import json
import sys
from collections import defaultdict, deque

COMPLEXITY_WEIGHT = {"simple": 1, "medium": 3, "complex": 8}
MAX_DEPTH = 3


def validate(tasks: list[dict]) -> dict:
    task_map = {t["id"]: t for t in tasks}
    adj = defaultdict(list)  # parent -> children
    in_degree = defaultdict(int)

    for t in tasks:
        tid = t["id"]
        if tid not in in_degree:
            in_degree[tid] = 0
        for dep in t.get("deps", []):
            adj[dep].append(tid)
            in_degree[tid] += 1

    # Kahn's BFS topological sort
    queue = deque([tid for tid in in_degree if in_degree[tid] == 0])
    topo_order = []

    while queue:
        node = queue.popleft()
        topo_order.append(node)
        for child in adj[node]:
            in_degree[child] -= 1
            if in_degree[child] == 0:
                queue.append(child)

    has_cycle = len(topo_order) != len(tasks)
    cycle_nodes = []
    if has_cycle:
        cycle_nodes = [tid for tid in in_degree if in_degree[tid] > 0]

    # Critical path (longest weighted path)
    dist = {tid: 0 for tid in topo_order}
    parent = {tid: None for tid in topo_order}

    for tid in topo_order:
        w = COMPLEXITY_WEIGHT.get(task_map[tid].get("complexity", "medium"), 3)
        for child in adj[tid]:
            if dist[tid] + w > dist.get(child, 0):
                dist[child] = dist[tid] + w
                parent[child] = tid

    # Trace back critical path from node with max distance
    if topo_order and not has_cycle:
        end_node = max(topo_order, key=lambda t: dist[t])
        critical_path = []
        node = end_node
        while node is not None:
            critical_path.append(node)
            node = parent[node]
        critical_path.reverse()
    else:
        critical_path = []

    # Depth: longest chain count (unweighted)
    depth = {}
    for tid in topo_order:
        deps = task_map[tid].get("deps", [])
        depth[tid] = (max((depth.get(d, 0) for d in deps), default=0) + 1) if not has_cycle else 0

    max_depth = max(depth.values(), default=0)

    # Spawn waves: group by topological level
    level = {}
    for tid in topo_order:
        deps = task_map[tid].get("deps", [])
        level[tid] = (max((level.get(d, 0) for d in deps), default=-1) + 1) if not has_cycle else 0

    waves = defaultdict(set)
    for tid, lvl in level.items():
        agent = task_map[tid].get("agent", tid)
        waves[lvl].add(agent)

    spawn_waves = [
        {"wave": w, "agents": sorted(waves[w])}
        for w in sorted(waves.keys())
    ]

    return {
        "has_cycle": has_cycle,
        "cycle_nodes": cycle_nodes,
        "critical_path": critical_path,
        "max_depth": max_depth,
        "max_depth_ok": max_depth <= MAX_DEPTH,
        "spawn_waves": spawn_waves,
    }


if __name__ == "__main__":
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON input: {e}"}))
        sys.exit(1)

    result = validate(data)
    print(json.dumps(result, indent=2))
