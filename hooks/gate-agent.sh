#!/bin/bash
# gate-agent.sh — Enforce worktree isolation for parallel agents
#
# Add to settings.json as a PreToolUse hook on the "Agent" tool.
# Blocks Agent spawns that edit code without worktree isolation,
# preventing broken imports, lost edits, and commit races.
#
# How it works:
# - Reads the Agent tool call JSON from stdin
# - If the agent prompt suggests editing files AND isolation != "worktree", blocks it
# - Passes through read-only/research agents without blocking

INPUT=$(cat)

# Extract isolation mode from the tool input
ISOLATION=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    params = data.get('tool_input', {})
    print(params.get('isolation', ''))
except:
    print('')
" 2>/dev/null)

# Extract the prompt to check if it's an editing agent
PROMPT=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    params = data.get('tool_input', {})
    print(params.get('prompt', ''))
except:
    print('')
" 2>/dev/null)

# Check if the prompt suggests file editing (write/edit/create/modify)
EDITS_FILES=$(echo "$PROMPT" | grep -iE '(write|edit|create|modify|implement|build|fix|refactor)\b' | head -1)

if [ -n "$EDITS_FILES" ] && [ "$ISOLATION" != "worktree" ]; then
    echo "BLOCK: Agent appears to edit files but isolation != 'worktree'."
    echo "Add isolation: \"worktree\" to prevent broken imports and commit races."
    echo "If this is a read-only agent, add 'read-only' or 'research' to the prompt."
    exit 2
fi

exit 0
