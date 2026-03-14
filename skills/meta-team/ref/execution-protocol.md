# Execution Protocol — Claude Code Teams API

> Grounded in: Claude Code team API, TDAG 2402.10178 (Kahn's ordering),
> DeMAC EMNLP 2025 (dynamic DAG), ZenML production findings

## API Reference

### TeamCreate
```
TeamCreate({ team_name: string, description: string })
```
Creates team + task list. One team per execution.

### TaskCreate
```
TaskCreate({ subject: string, description: string, activeForm: string })
```
Creates task with status `pending`. `activeForm` = spinner text (present continuous).

### TaskUpdate
```
TaskUpdate({
  taskId: string,
  status?: "pending" | "in_progress" | "completed",
  owner?: string,
  addBlockedBy?: string[],
  addBlocks?: string[],
  subject?: string,
  description?: string
})
```
Set dependencies AFTER creation. Assign owner when spawning agent.

### TaskGet / TaskList
```
TaskGet({ taskId: string })
TaskList({})
```

### SendMessage
```
// Direct message
SendMessage({ type: "message", recipient: "agent-name", content: "...", summary: "5-10 words" })

// Broadcast (expensive — N agents = N messages)
SendMessage({ type: "broadcast", content: "...", summary: "..." })

// Shutdown
SendMessage({ type: "shutdown_request", recipient: "agent-name", content: "..." })
```

### Agent (spawn)
```
Agent({
  subagent_type: "general-purpose",
  team_name: string,
  name: string,
  model: "haiku" | "sonnet" | "opus",
  isolation: "worktree",
  prompt: string,
  description: string  // 3-5 words
})
```
Always `isolation: "worktree"` for team workers.

### TeamDelete
```
TeamDelete({})
```
Fails if active members. Shutdown all first.

## Spawn Wave Algorithm

```
1. TeamCreate(team_name, description)
2. TaskCreate for ALL tasks (topological order)
3. TaskUpdate to set all dependencies (addBlockedBy)
4. For each wave in spawn_waves:
   a. For each agent in wave.agents:
      - Generate spawn prompt (ref/spawn-template.md)
      - Screen against failure modes (ref/failure-modes.md)
      - Spawn via Agent tool
      - TaskUpdate to assign ownership
   b. Monitor via TaskList until wave tasks complete
   c. Task fails → retry once → still fails → alert user
5. All waves complete → Phase 6 (JUDGE)
```

## Task Lifecycle

```
pending → in_progress → completed
                     ↘ blocked (via addBlockedBy)
                     ↘ split (lead creates subtasks, deletes original)
```

Workers must:
1. `TaskUpdate(status: "in_progress")` — when starting
2. Work on task
3. `TaskUpdate(status: "completed")` — when acceptance criteria met
4. `SendMessage` to lead — completion summary

## Circuit Breakers

| Trigger | Action |
|---------|--------|
| Cost >80% budget | Alert user, offer model downgrade |
| Worker idle >5min | Diagnostic SendMessage |
| Worker idle >7min | Reassign task to new agent |
| Message depth >20 without progress | STOP agents, alert user |
| Worker reports task too large | Split: create subtasks, update deps |

## Shutdown Lifecycle

```
1. All tasks completed (or user aborts)
2. Shutdown workers in reverse wave order
3. Shutdown judge (if running)
4. TeamDelete()
```

## Error Handling

| Error | Action |
|-------|--------|
| Spawn fails | Retry once. If fails again → alert user |
| Task blocked indefinitely | Check dep chain. Circular → alert user |
| Wrong files modified | FM-1.2 mitigation. Message + correct. If persistent → reassign |
| Tests fail on completion | Reject completion. Worker must fix |
| Budget exhausted | Stop all. Present partial results |
| User aborts | Broadcast shutdown. Clean up. TeamDelete |
