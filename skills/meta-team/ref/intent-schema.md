# Intent Schema — W5H2 Decomposition

> Grounded in: W5H2 2602.18922 (91.1% accuracy at 2ms), Ambig-SWE 2502.13069
> (Claude 89% spec gap detection), "What Prompts Don't Say" 2505.13360

## W5H2 Fields

| Field | Key | Required | Extraction Question |
|-------|-----|----------|-------------------|
| Who | agents | yes | Who will do the work? (agent roles, not humans) |
| What | deliverables | yes | What are the concrete outputs? |
| When | sequence | no | What depends on what? (ordering, not dates) |
| Where | files | yes | Which files/dirs are created or modified? |
| Why | objective | yes | What problem does this solve? |
| How | approach | yes | What tools, frameworks, patterns? |
| How Much | budget | no | Token budget, model tiers, time constraints? |

## Deliverable Structure

Each deliverable becomes a JSON object:

```json
{
  "name": "API client module",
  "description": "Typed fetch wrappers for all endpoints",
  "files": ["src/lib/api.ts", "src/lib/types.ts"],
  "tools": ["Write", "Bash"],
  "acceptance": "No raw fetch() calls in components",
  "complexity": "medium",
  "deps": []
}
```

## Decomposability Heuristics

**Independence signals** (increase decomposability):
- Deliverables touch different directories
- No shared type definitions or imports between deliverables
- Each deliverable has its own test surface
- Deliverables map to different skill domains

**Coupling signals** (decrease decomposability):
- Multiple deliverables modify the same file
- Shared state or configuration objects
- Import chains between deliverables
- Ordering constraints ("X must exist before Y can start")

## Spec Completeness Check

Classify each underspecified field:

| Category | Action | Example |
|----------|--------|---------|
| **Outcome-critical** | STOP — ask user | "Make it fast" (no target metric) |
| **Divergent** | FLAG — present default + ask | "Use a database" (which one?) |
| **Benign** | PROCEED — use sensible default | "Pick a testing framework" |

### Outcome-Critical Patterns
- Performance target without metric ("make it fast", "optimize")
- Scope boundary missing ("clean up the code" — which code?)
- Success criteria absent ("improve the UI" — compared to what?)
- Conflicting constraints (mobile-first + desktop-only features)

### Divergent Patterns
- Technology choice left open ("use a framework")
- Architecture decision implied but not stated ("make it scalable")
- Multiple valid interpretations of a requirement

### Benign Gaps
- Style/formatting preferences
- Test framework choice when tests aren't the focus
- File naming conventions within a new directory

## Worked Examples

### Example 1: Vague Prompt
**Input:** "Make our app better"
**Extraction:**
- What: MISSING (outcome-critical — stop)
- Where: MISSING
- How: MISSING
- **Action:** Ask user. Cannot decompose.

### Example 2: Detailed Prompt
**Input:** "Rewrite dashboard from monolith HTML to React + shadcn/ui. Keep FastAPI backend. 6 deliverables: scaffold, layout, overview page, strategy page, backtest page, API client."
**Extraction:**
- Who: 4-5 agents (scaffold, layout, pages, API)
- What: 6 deliverables with clear boundaries
- Where: src/dashboard/frontend/ (new), src/dashboard/app.py (frozen)
- Why: Replace innerHTML spaghetti with component architecture
- How: Vite + React + TypeScript + shadcn/ui
- How Much: Not specified (benign — estimate via budget.py)
- **Decomposability: 0.72** (independent pages, shared API client)

### Example 3: Existing Codebase
**Input:** "Add authentication to the Express API"
**Extraction:**
- Who: 1-2 agents (auth module + integration)
- What: Auth middleware, login/register endpoints, session management
- Where: Needs codebase exploration to determine
- How: DIVERGENT — JWT vs sessions vs OAuth (ask user)
- **Action:** Explore codebase first, then flag divergent choices.

## Anti-Patterns

### Over-Extraction
- Splitting a single function into 3 deliverables
- Creating deliverables for imports, types, and config separately
- Treating "write tests" as a separate deliverable per file

### Under-Extraction
- "Build the frontend" as one deliverable (too large)
- Combining unrelated features because they're in the same file
- Hiding infrastructure work inside a feature deliverable
