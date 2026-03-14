# Failure Modes — MAST Taxonomy

> Grounded in: MAST 2503.13657 (14 failure modes, inter-rater kappa=0.88),
> ZenML production findings ($47K runaway agent), IBM 2511.10650 (cycle detection)

## Taxonomy

### FC1: Agent-Task Alignment (5 modes)

| ID | Name | Description | Frequency |
|----|------|-------------|-----------|
| FM-1.1 | Spec Disobedience | Agent ignores or contradicts explicit task requirements | High |
| FM-1.2 | Role Confusion | Agent acts outside its assigned role, modifies unowned files | Medium |
| FM-1.3 | Step Repetition | Agent repeats the same action in a loop without progress | Medium |
| FM-1.4 | History Loss | Agent forgets earlier context, contradicts own previous output | Low |
| FM-1.5 | Termination Unawareness | Agent doesn't know when to stop, keeps "improving" | High |

### FC2: Communication (6 modes)

| ID | Name | Description | Frequency |
|----|------|-------------|-----------|
| FM-2.1 | Conversation Reset | Agent loses thread of multi-turn conversation | Low |
| FM-2.2 | Clarification Failure | Agent proceeds despite ambiguity instead of asking | High |
| FM-2.3 | Derailment | Agent goes off-topic, explores tangential concerns | Medium |
| FM-2.4 | Info Withholding | Agent has relevant info but doesn't share with team | Low |
| FM-2.5 | Ignored Input | Agent ignores steering messages from lead | Medium |
| FM-2.6 | Reasoning-Action Mismatch | Agent reasons correctly but takes wrong action | Low |

### FC3: Verification (3 modes)

| ID | Name | Description | Frequency |
|----|------|-------------|-----------|
| FM-3.1 | Premature Termination | Agent declares done before all acceptance criteria met | High |
| FM-3.2 | Incomplete Verification | Agent checks some but not all criteria | Medium |
| FM-3.3 | Incorrect Verification | Agent misinterprets pass/fail of verification checks | Low |

## Mitigation Templates

Inject into `<mitigations>` section of spawn prompts. Screen each agent against all 14 modes; inject for modes rated Medium or High risk.

### FM-1.1: Spec Disobedience
```
Before marking any task complete, re-read the <tasks> section and verify each
acceptance criterion is met. List each criterion and its status in your completion message.
```

### FM-1.2: Role Confusion
```
You may ONLY create or modify files listed in your <files> OWN section.
If you need changes to a file you don't own, message the lead with the
specific change needed. Never modify read-only files.
```

### FM-1.3: Step Repetition
```
If the same tool call fails twice with the same error, STOP. Do not retry.
Message the lead with: the action attempted, the error, and a proposed alternative.
```

### FM-1.4: History Loss
```
If you are unsure about a decision made earlier in the conversation, re-read
your <tasks> and <constraints> sections rather than guessing.
```

### FM-1.5: Termination Unawareness
```
Your work is DONE when all tasks in <tasks> pass their acceptance criteria.
Do not refactor, optimize, add comments, or "improve" beyond what is specified.
Mark task complete and stop.
```

### FM-2.1: Conversation Reset
```
If you receive a message that seems to restart the conversation, check TaskGet
for your current task status before responding.
```

### FM-2.2: Clarification Failure
```
If a requirement has two valid interpretations, message the lead with both
options and your recommendation. Do not guess. Guessing costs more than asking.
```

### FM-2.3: Derailment
```
Stay focused on files and tasks in your <files> and <tasks> sections.
If you discover related issues outside your scope, note them in your completion
message but do not attempt to fix them.
```

### FM-2.4: Info Withholding
```
If you discover information that other agents need (API shape, type definitions,
gotchas), send a message to the lead immediately. Don't wait until completion.
```

### FM-2.5: Ignored Input
```
When you receive a message from the lead, acknowledge it and adjust your approach.
If you disagree with the steering, explain why before proceeding differently.
```

### FM-2.6: Reasoning-Action Mismatch
```
Before executing a tool call, state what you intend to do and why in one sentence.
This creates an audit trail and catches reasoning-action mismatches.
```

### FM-3.1: Premature Termination
```
Before marking complete, run through this checklist:
□ All files in <files> OWN created/modified as specified
□ Each task in <tasks> has acceptance criteria met
□ No TypeScript/lint errors in owned files
□ Completion message lists FILES, TESTS, DEVIATIONS
```

### FM-3.2: Incomplete Verification
```
Verify EVERY acceptance criterion, not just the first or most obvious one.
List each criterion with PASS/FAIL in your completion message.
```

### FM-3.3: Incorrect Verification
```
When checking acceptance criteria, use tool calls (Bash, Read) to verify —
do not rely on memory of what you wrote. Read the actual file content.
```

## Screening Checklist

For each agent, score risk per FM:

```
Agent: {name}
Task complexity: {simple|medium|complex}

| FM | Risk | Inject? | Rationale |
|----|------|---------|-----------|
| 1.1 | H/M/L | Y/N | {why} |
| ... | ... | ... | ... |

Mitigations to inject: FM-{X.Y}, FM-{X.Y}, ...
```

**Default high-risk (inject for ALL agents):**
- FM-1.1 (spec disobedience)
- FM-1.5 (termination unawareness)
- FM-3.1 (premature termination)

**Task-specific escalation:**
- Touches shared files → FM-1.2
- Complex multi-step → FM-1.3
- Ambiguous requirements → FM-2.2
- Output consumed by others → FM-2.4
