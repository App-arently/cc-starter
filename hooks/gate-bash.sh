#!/bin/bash
# gate-bash.sh — Block dangerous shell commands
#
# Add to settings.json as a PreToolUse hook on the "Bash" tool.
# Catches obviously destructive commands before they execute.
#
# Blocked patterns:
# - rm -rf / (or variations)
# - chmod 777
# - git push --force to main/master
# - dd if= of=/dev/
# - mkfs on real devices
# - DROP DATABASE / DROP TABLE without confirmation

INPUT=$(cat)

# Extract the command from the tool input
COMMAND=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    params = data.get('tool_input', {})
    print(params.get('command', ''))
except:
    print('')
" 2>/dev/null)

# Check for dangerous patterns
check_dangerous() {
    local cmd="$1"

    # rm -rf / or rm -rf /*
    if echo "$cmd" | grep -qE 'rm\s+(-[a-zA-Z]*f[a-zA-Z]*\s+|--force\s+).*(/\s*$|/\*|/\.\.)'; then
        echo "BLOCK: Refusing to run 'rm -rf' on root or near-root paths."
        return 1
    fi

    # chmod 777 on anything
    if echo "$cmd" | grep -qE 'chmod\s+777'; then
        echo "BLOCK: chmod 777 is a security risk. Use specific permissions (e.g., 755, 644)."
        return 1
    fi

    # git push --force to main/master
    if echo "$cmd" | grep -qE 'git\s+push\s+.*--force.*\s+(main|master)'; then
        echo "BLOCK: Force-pushing to main/master can destroy shared history."
        return 1
    fi
    if echo "$cmd" | grep -qE 'git\s+push\s+.*\s+(main|master)\s+.*--force'; then
        echo "BLOCK: Force-pushing to main/master can destroy shared history."
        return 1
    fi

    # dd to block devices
    if echo "$cmd" | grep -qE 'dd\s+.*of=/dev/[sh]d'; then
        echo "BLOCK: Writing directly to block devices can destroy data."
        return 1
    fi

    # mkfs on real devices
    if echo "$cmd" | grep -qE 'mkfs.*\s+/dev/[sh]d'; then
        echo "BLOCK: Formatting block devices can destroy data."
        return 1
    fi

    # SQL drops without caution
    if echo "$cmd" | grep -qiE '(DROP\s+DATABASE|DROP\s+TABLE)'; then
        echo "BLOCK: DROP DATABASE/TABLE detected. This is destructive and irreversible."
        return 1
    fi

    return 0
}

if ! check_dangerous "$COMMAND"; then
    exit 2
fi

exit 0
