---
name: meta-team
description: "Decompose intent and orchestrate Claude Code agent teams. 7-phase pipeline: assess → decompose → topology → generate → execute → adapt → judge. Triggers on: meta-team, compile a team, spawn a team, build a team, assemble a team, wire a team."
argument-hint: [objective]
---

# Meta-Team

Intent decomposer first. Team spawner second.

Transform a natural language prompt into a validated, executing agent team using Claude Code native APIs (TeamCreate, TaskCreate, SendMessage, Agent).

## Pipeline

```
Phase 0: ASSESS       Decomposability score, team-or-not gate
Phase 1: DECOMPOSE    W5H2 intent extraction, spec completeness
    ═══ CHECKPOINT 1: Intent + score + recommendation ═══
Phase 2: TOPOLOGY     Agent roles, file ownership, DAG, cost
    ═══ CHECKPOINT 2: Team table + DAG + cost ═══
Phase 3: GENERATE     Spawn prompts + MAST mitigations + SCAN anchors
Phase 4: EXECUTE      TeamCreate → TaskCreate → spawn in waves
Phase 5: ADAPT        Circuit breakers, reassignment, model downgrade
Phase 6: JUDGE+LEARN  Independent judge, reconciliation, post-mortem
```

---

## Phase 0: ASSESS

Read execution history and score the prompt.

1. Read `memory/post-mortems.jsonl` — extract patterns from prior runs
2. Read `memory/autonomy.json` — current autonomy level (conservative/standard/autonomous)
3. If existing codebase mentioned → explore with Glob/Grep/Read to build context
4. Build assessment input:
   ```json
   {
     "objective": "<extracted from prompt>",
     "deliverables": [{"name": "...", "files": [], "tools": []}],
     "constraints": [],
     "existing_codebase": true|false
   }
   ```
5. Run: `echo '<json>' | python3 ~/.claude/skills/meta-team/scripts/assess.py`
6. Read output: `{decomposability, tool_density, recommendation, reasoning}`

**Decision gate:**
- Score <0.45 → recommend solo + subagents (use `subagent-driven-development` skill)
- Score ≥0.45 → proceed to Phase 1
- Ask user if recommendation differs from their expectation

---

## Phase 1: DECOMPOSE INTENT

Extract structured intent using W5H2 framework. Reference: `ref/intent-schema.md`

1. **W5H2 extraction** from user prompt:
   - **Who:** Agent roles needed
   - **What:** Concrete deliverables with acceptance criteria
   - **When:** Dependencies/ordering between deliverables
   - **Where:** Files/directories created or modified
   - **Why:** Problem being solved
   - **How:** Tools, frameworks, patterns, architecture
   - **How Much:** Budget, model tiers, constraints

2. **Two-stage decomposition:**
   - First: summarize each deliverable independently as JSON
   - Then: aggregate, check for cross-deliverable coupling

3. **Spec completeness check** (ref/intent-schema.md):
   - **Outcome-critical gaps** → STOP, ask user
   - **Divergent gaps** → FLAG with default, present to user
   - **Benign gaps** → PROCEED with sensible default

4. Output structured JSON intent (not prose)

### CHECKPOINT 1

Present to user:
- Structured intent (W5H2 summary)
- Decomposability score + reasoning
- Recommendation: team or single agent
- Any flagged spec gaps

**Skip conditions:** Autonomy level "standard" or higher AND decomposability >0.7 AND no outcome-critical gaps.

---

## Phase 2: TOPOLOGY

Map deliverables to agents, build DAG, estimate cost. Reference: `ref/topology-patterns.md`

1. **Select topology** based on task shape:
   | Pattern | When |
   |---------|------|
   | Solo + subagents | decomposability <0.45 or <3 tasks |
   | Hub-spoke | 3-5 independent streams |
   | Pipeline | Sequential chain |
   | Hybrid | Foundation wave + integration wave |

2. **Map deliverables → agents:**
   - One owner per file (invariant, no exceptions)
   - Lead owns shared files (types, config, routing)
   - Model tier per agent: haiku (scaffold), sonnet (implementation), opus (architecture)

3. **Build task DAG:**
   - Max depth 2-3, max 6 tasks per agent
   - Foundation tasks in Wave 0

4. **Validate DAG:**
   ```bash
   echo '<tasks_json>' | python3 ~/.claude/skills/meta-team/scripts/validate_dag.py
   ```
   - Check: no cycles, depth ≤3, spawn waves computed
   - If cycles detected → restructure before proceeding

5. **Estimate budget:**
   ```bash
   echo '<budget_json>' | python3 ~/.claude/skills/meta-team/scripts/budget.py
   ```
   - Per-agent token/cost estimate
   - Total: optimistic, expected, pessimistic
   - Meta overhead (planning + judging)

### CHECKPOINT 2

Present to user:
- Team table: agent name, model, files owned, tasks
- DAG visualization (text): waves, dependencies
- File ownership map
- Cost estimate (optimistic / expected / pessimistic)

**Skip conditions:** Autonomy level "autonomous" AND no budget concerns AND DAG validates clean.

---

## Phase 3: GENERATE

Write spawn prompts for each agent. Reference: `ref/spawn-template.md`, `ref/failure-modes.md`

1. **For each agent**, build XML-tagged spawn prompt:
   ```
   <role> <context> <files> <tasks> <communication> <constraints> <mitigations> <scan>
   ```

2. **Screen against failure modes** (ref/failure-modes.md):
   - Always inject: FM-1.1 (spec disobedience), FM-1.5 (termination unawareness), FM-3.1 (premature termination)
   - Task-specific: FM-1.2 if shared files, FM-1.3 if complex multi-step, FM-2.2 if ambiguous requirements

3. **Add SCAN anchors** (3-5 questions at prompt end):
   - Agent must answer before starting work
   - Questions target: role clarity, file ownership, task scope, communication protocol
   - <0.5% token overhead, prevents context drift

4. **Length check:**
   - haiku agents: <500 words
   - sonnet agents: 500-1500 words
   - Trim context section first if over budget

---

## Phase 4: EXECUTE

Launch the team using Claude Code native APIs. Reference: `ref/execution-protocol.md`

```
Step 1: TeamCreate(team_name, description)
Step 2: TaskCreate for ALL tasks in topological order
Step 3: TaskUpdate to set dependencies (addBlockedBy for each task)
Step 4: For each spawn wave:
  4a. Spawn agents via Agent tool:
      - subagent_type: "general-purpose"
      - team_name: from Step 1
      - name: agent role name
      - model: from topology (haiku/sonnet/opus)
      - isolation: "worktree"
      - prompt: generated spawn prompt from Phase 3
  4b. TaskUpdate to assign ownership (owner = agent name)
  4c. Monitor wave completion via TaskList
  4d. If task fails: retry once → if still fails, alert user
Step 5: After all waves → Phase 5 monitoring or Phase 6 judging
```

**Spawn wave rules:**
- Wave 0: immediately (foundation/scaffold tasks)
- Wave N+1: after all Wave N tasks complete
- Agents within a wave launch in parallel

---

## Phase 5: ADAPT

Runtime monitoring and intervention. Reference: `ref/execution-protocol.md`

### Circuit Breakers

| Trigger | Action |
|---------|--------|
| Cost >80% budget | Alert user, offer model downgrade |
| Worker idle >5min | Diagnostic message via SendMessage |
| Worker idle >7min | Reassign task to new agent |
| Message depth >20 without progress | STOP agents, alert user |
| Worker reports task too large | Split task: create subtasks, update dependencies |

### Monitoring Loop

```
While tasks remain incomplete:
  1. TaskList() — check status of all tasks
  2. For each in_progress task:
     - Check if blocked or stalled
     - Apply circuit breakers if triggered
  3. For each completed task:
     - Verify deliverable files exist (Glob check)
     - If Wave N complete → spawn Wave N+1 agents
  4. If all tasks complete → proceed to Phase 6
```

---

## Phase 6: JUDGE + LEARN

Independent quality assessment and cross-session learning.

### Judge Agent

Spawn an **independent judge** with ISOLATED context:
- Model: opus (always)
- Context: original intent JSON + file ownership map + delivered files
- **Never** shares producing agents' conversation history
- Examines full trajectory (files created, not just final state)

Judge evaluates:
- Per-requirement: Delivered / Partial / Missed
- Code quality: patterns followed, no dead code, tests pass
- Deviations from spec: justified or accidental

### PRD Reconciliation

```
For each requirement in original intent:
  - DELIVERED: acceptance criteria fully met
  - PARTIAL: implemented but criteria not fully met
  - MISSED: not implemented
```

Present reconciliation to user. If any Partial/Missed:
- Option A: re-plan gaps with new team
- Option B: file as follow-up tasks
- Option C: accept as-is

### Post-Mortem

Write to `memory/post-mortems.jsonl`:
```json
{"date":"ISO","objective":"str","team_size":N,"topology":"str","tasks_total":N,"delivered":N,"partial":N,"missed":N,"cost_estimated":0.0,"cost_actual":0.0,"duration_min":N,"failure_modes_hit":["FM-X.Y"],"lesson":"str"}
```

### Autonomy Update

Update `memory/autonomy.json`:
- All delivered + cost ≤120% estimate → `consecutive_successes += 1`
- Any missed OR cost >150% estimate → `consecutive_successes = 0`
- Levels: conservative (0-2), standard (3-6), autonomous (7+)

Autonomy affects checkpoints:
- **conservative:** Both checkpoints mandatory
- **standard:** Checkpoint 1 skippable if decomposability >0.7
- **autonomous:** Both checkpoints skippable (still logged)

---

## Red Flags — Stop and Ask User

- Decomposability <0.3 but user wants a team
- More than 15 tasks in DAG
- Cycles detected in task graph
- Multiple agents claiming same file
- Budget pessimistic >$10 without acknowledgment
- Outcome-critical spec gaps in Phase 1
- Worker fails same task twice

## Key Rules

1. **Intent first, team second.** Never spawn agents before intent is fully decomposed.
2. **One owner per file.** No exceptions. Conflicts → restructure.
3. **Scripts for math, LLM for reasoning.** Never LLM-judge what a script can verify.
4. **Judge is isolated.** Never sees producing agents' context.
5. **Deterministic gates.** assess.py, validate_dag.py, budget.py — trust their output.
6. **SCAN every agent.** 3-5 questions at end of every spawn prompt.
7. **Retry once, then escalate.** Never retry the same failing action more than once.
8. **Match model to task.** haiku for scaffold, sonnet for logic, opus for architecture.
9. **Log everything.** Post-mortem after every run. Autonomy graduates on track record.
10. **User sees the plan.** Checkpoints mandatory until autonomy proves otherwise.
