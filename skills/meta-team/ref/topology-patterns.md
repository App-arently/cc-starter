# Topology Patterns

> Grounded in: MALBO 2511.11788 (Bayesian team optimization),
> Cursor blog (Planner-Worker-Judge at 1M lines)

## Pattern Selection

| Pattern | When | Agents | Example |
|---------|------|--------|---------|
| **Solo + Subagents** | decomposability <0.45 or <3 tasks | 1 lead + N haiku | Refactor a single module |
| **Hub-Spoke** | 3-5 independent streams | 1 lead + N workers | Dashboard pages (each independent) |
| **Pipeline** | Sequential chain, each feeds next | N agents in series | ETL: extract → transform → load |
| **Hybrid** | Foundation wave + integration wave | N parallel → 1 integrator | Scaffold → parallel pages → final wiring |

## Solo + Subagents

Lead agent does primary work, delegates read-heavy or boilerplate tasks to haiku subagents.

```
Lead (opus/sonnet)
 ├── Subagent: explore codebase (haiku)
 ├── Subagent: generate types (haiku)
 └── Subagent: write tests (haiku)
```

**Select when:**
- High file coupling (many shared files)
- <3 distinct deliverables
- Tight integration requirements
- Decomposability score <0.45

## Hub-Spoke

Lead coordinates, workers execute independently. Lead resolves conflicts.

```
Lead (opus) ─── coordinates
 ├── Worker A (sonnet) ─── page/feature 1
 ├── Worker B (sonnet) ─── page/feature 2
 ├── Worker C (sonnet) ─── page/feature 3
 └── Worker D (haiku)  ─── config/scaffold
```

**Select when:**
- 3-5 independent streams with minimal coupling
- Each worker owns distinct files
- Lead handles shared files (types, config, routing)
- Decomposability score >0.6

## Pipeline

Each agent's output feeds the next. Strict ordering.

```
Agent A → Agent B → Agent C → Agent D
(scaffold)  (core)   (features) (tests)
```

**Select when:**
- Strong sequential dependencies
- Each stage produces artifacts the next consumes
- Cannot parallelize without significant rework risk

## Hybrid

Most common for real projects. Foundation wave runs parallel, integration wave sequential.

```
Wave 0: scaffold (haiku)
Wave 1: [page-A, page-B, api-client] (sonnet, parallel)
Wave 2: integrator (sonnet, sequential)
Wave 3: judge (opus, independent)
```

**Select when:**
- Mix of independent and dependent work
- Clear foundation layer needed first
- Integration/wiring step at the end
- Decomposability 0.5-0.8

## Model Tier Routing

| Tier | Model | Use For | Token Budget |
|------|-------|---------|-------------|
| **haiku** | claude-haiku-4-5 | Scaffold, config, boilerplate, exploration | <500 word prompts |
| **sonnet** | claude-sonnet-4-6 | Implementation, logic, integration | 500-1500 word prompts |
| **opus** | claude-opus-4-6 | Architecture decisions, judging, complex reasoning | Full context |

**Routing rules:**
- If task creates files from a template → haiku
- If task implements business logic or integrates components → sonnet
- If task requires design decisions or quality judgment → opus
- Lead/orchestrator is always opus
- Judge is always opus with isolated context

## File Ownership Rules

**Invariant: One owner per file. No exceptions.**

| Rule | Detail |
|------|--------|
| Single owner | Each file has exactly one agent responsible for creating/modifying it |
| Read-only access | Other agents may READ owned files but never WRITE |
| Shared directories | Lead or integrator owns shared dirs (types/, config/) |
| Conflict resolution | If two deliverables need the same file → either merge deliverables or split file |
| Integration files | Router, main entry point → owned by integrator in final wave |

## DAG Constraints

| Constraint | Limit | Rationale |
|-----------|-------|-----------|
| Max tasks per agent | 6 | Beyond 6, context window degrades quality |
| Max DAG depth | 3 | Deeper chains increase latency and failure cascade risk |
| Foundation tasks | Required | Wave 0 must include scaffold/config that others depend on |
| Cycle detection | Must pass | Run validate_dag.py — cycles cause infinite waits |
| Critical path | Minimize | Longest chain determines total execution time |
