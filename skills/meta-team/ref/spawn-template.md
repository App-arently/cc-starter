# Spawn Prompt Template

> Grounded in: SCAN technique (HuggingFace — attention restoration ~1% → ~50%),
> MAST 2503.13657 (14 FM, kappa=0.88), Anthropic spawn prompt guidance

## XML-Tagged Structure

Every spawn prompt uses this structure. Tags are mandatory. Order matters.

```xml
<role>
{agent_name} — {one-line purpose}
You are part of team "{team_name}". Your lead is "{lead_name}".
</role>

<context>
{2-3 sentences: what the project is, current state, what's been done}
{If existing codebase: key patterns, naming conventions, test framework}
</context>

<files>
You OWN (create/modify):
- {path/to/file1} — {purpose}
- {path/to/file2} — {purpose}

You may READ (do not modify):
- {path/to/shared/types.ts} — shared type definitions
- {path/to/config.ts} — project configuration
</files>

<tasks>
1. {Task description with specific acceptance criteria}
2. {Task description with specific acceptance criteria}
...
</tasks>

<communication>
- Report progress via TaskUpdate (mark in_progress when starting, completed when done)
- If blocked: send message to lead with specific blocker description
- If task is too large: send message to lead requesting split
- On completion: update task status, send summary to lead
</communication>

<constraints>
- {Constraint 1: e.g., "Do not modify app.py"}
- {Constraint 2: e.g., "Use TypeScript strict mode"}
- {Constraint 3: e.g., "All components must be function components with hooks"}
</constraints>

<mitigations>
{Injected from failure-modes.md screening — see below}
</mitigations>

<scan>
Before starting work, answer these questions in your first message to the lead:
1. {Question targeting role clarity}
2. {Question targeting file ownership understanding}
3. {Question targeting task scope}
</scan>
```

## Length Guidelines

| Model Tier | Max Words | Sections to Emphasize |
|-----------|-----------|----------------------|
| haiku | <500 | role, files, tasks (minimal context) |
| sonnet | 500-1500 | All sections, moderate detail |
| opus | 1500+ | Full context, architectural rationale |

## SCAN Anchors

3-5 questions placed at the END of the prompt. Agent must answer before starting work.

**Purpose:** Prevents context drift in long sessions. Forces agent to re-attend to critical constraints. <0.5% token overhead, ~50x attention restoration.

**Good SCAN questions:**
- "What files do you OWN and what files are READ-ONLY?"
- "What is the acceptance criteria for your first task?"
- "What should you do if you need to modify a file you don't own?"
- "What framework and patterns are you using?"
- "When should you message the lead vs continue working?"

**Bad SCAN questions:**
- "Are you ready?" (no information)
- "What is the project?" (too broad, wastes tokens)
- "Do you understand?" (yes/no, no verification)

## Good Example

```xml
<role>
api-client — Build typed API client for all FastAPI endpoints
You are part of team "dashboard-rewrite". Your lead is "team-lead".
</role>

<context>
We're rewriting a trading dashboard from a 2461-line HTML monolith to React + shadcn/ui.
The FastAPI backend (app.py) has 23 active endpoints. Backend is frozen — no modifications.
Patterns: TypeScript strict, function components, @tanstack/react-query for data fetching.
</context>

<files>
You OWN:
- src/frontend/lib/api.ts — API client with typed fetch wrappers
- src/frontend/lib/types.ts — TypeScript interfaces matching API responses

You may READ:
- src/dashboard/app.py — endpoint definitions (DO NOT MODIFY)
</files>

<tasks>
1. Read app.py to extract all 23 active endpoint signatures (method, path, response shape)
2. Write TypeScript interfaces in types.ts matching each endpoint's response
3. Write api.ts with typed fetch functions — one per endpoint, using base URL from env
4. Export a query key factory for @tanstack/react-query integration
Acceptance: No raw fetch() calls needed in components. All endpoints covered.
</tasks>

<communication>
- Report progress via TaskUpdate
- If an endpoint response shape is ambiguous, message lead with the specific endpoint
- On completion: list all exported functions and types
</communication>

<constraints>
- No axios — use native fetch with typed wrappers
- All functions must handle error responses (non-2xx) with typed error objects
- Base URL from environment variable, not hardcoded
</constraints>

<mitigations>
- FM-1.1 (spec disobedience): Re-read <tasks> acceptance criteria before marking complete
- FM-3.1 (premature termination): Verify all 23 endpoints are covered before completing
</mitigations>

<scan>
Before starting, answer:
1. How many endpoints should your API client cover?
2. What file must you READ but never MODIFY?
3. What data fetching library will components use with your client?
</scan>
```

## Bad Example (Anti-Patterns)

```
You are a helpful assistant. Please build an API client for our project.
Look at app.py and create types. Make sure it works well.
Let me know when you're done.
```

**Problems:**
- No role/team context
- No file ownership
- No acceptance criteria
- No constraints
- No SCAN anchors
- "works well" is unmeasurable
