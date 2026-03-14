#!/bin/bash
set -euo pipefail

# cc-starter installer
# Symlinks skills into ~/.claude/skills/, copies templates, wires hooks.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR="$HOME/.claude"
SKILLS_DIR="$CLAUDE_DIR/skills"

echo "=== cc-starter installer ==="
echo ""

# 1. Create ~/.claude/skills/ if missing
if [ ! -d "$SKILLS_DIR" ]; then
    echo "Creating $SKILLS_DIR..."
    mkdir -p "$SKILLS_DIR"
fi

# 2. Symlink each skill directory
SKILLS=(
    brainstorming
    mirror
    killbloat
    elai-5
    elai-18
    elai-65
    review
    knowledge-cache
    ship
    qa
    meta-team
)

echo "Installing skills..."
installed=0
skipped=0

for skill in "${SKILLS[@]}"; do
    src="$SCRIPT_DIR/skills/$skill"
    dest="$SKILLS_DIR/$skill"

    if [ -L "$dest" ]; then
        # Already a symlink — check if it points to us
        current_target=$(readlink -f "$dest" 2>/dev/null || true)
        expected_target=$(readlink -f "$src" 2>/dev/null || true)
        if [ "$current_target" = "$expected_target" ]; then
            echo "  [skip] $skill (already linked)"
            ((skipped++))
            continue
        else
            echo "  [update] $skill (relinking)"
            rm "$dest"
        fi
    elif [ -d "$dest" ]; then
        echo "  [skip] $skill (directory exists — not overwriting)"
        ((skipped++))
        continue
    fi

    ln -s "$src" "$dest"
    echo "  [link] $skill -> $src"
    ((installed++))
done

# 3. Copy CLAUDE.md.template (only if no CLAUDE.md exists)
if [ ! -f "$CLAUDE_DIR/CLAUDE.md" ]; then
    cp "$SCRIPT_DIR/CLAUDE.md.template" "$CLAUDE_DIR/CLAUDE.md"
    echo ""
    echo "Copied CLAUDE.md.template -> ~/.claude/CLAUDE.md"
else
    echo ""
    echo "~/.claude/CLAUDE.md already exists — not overwriting."
    echo "  Review CLAUDE.md.template for ideas to merge into yours."
fi

# 4. Copy hooks into skills dir for settings.json to reference
HOOKS_DEST="$SKILLS_DIR/hooks"
if [ ! -d "$HOOKS_DEST" ]; then
    mkdir -p "$HOOKS_DEST"
fi
cp "$SCRIPT_DIR/hooks/gate-agent.sh" "$HOOKS_DEST/gate-agent.sh"
cp "$SCRIPT_DIR/hooks/gate-bash.sh" "$HOOKS_DEST/gate-bash.sh"
chmod +x "$HOOKS_DEST/gate-agent.sh" "$HOOKS_DEST/gate-bash.sh"
echo "Installed hooks to $HOOKS_DEST"

# 5. Initialize meta-team memory (empty starting state)
META_MEMORY="$SKILLS_DIR/meta-team/memory"
if [ -L "$SKILLS_DIR/meta-team" ]; then
    # Resolve through symlink
    META_MEMORY="$(readlink -f "$SKILLS_DIR/meta-team")/memory"
fi

if [ ! -f "$META_MEMORY/autonomy.json" ]; then
    mkdir -p "$META_MEMORY"
    echo '{"level":"conservative","consecutive_successes":0}' > "$META_MEMORY/autonomy.json"
    echo "Initialized meta-team autonomy.json"
fi
if [ ! -f "$META_MEMORY/post-mortems.jsonl" ]; then
    touch "$META_MEMORY/post-mortems.jsonl"
    echo "Initialized meta-team post-mortems.jsonl"
fi

# 6. Summary
echo ""
echo "=== Installation complete ==="
echo "  Skills installed: $installed"
echo "  Skills skipped:   $skipped"
echo "  Total available:  ${#SKILLS[@]}"
echo ""
echo "To enable safety hooks, merge settings-hooks.json into your"
echo "~/.claude/settings.json (or project .claude/settings.json)."
echo ""
echo "Quick start:"
echo "  /brainstorming    — explore ideas before building"
echo "  /elai-5           — explain code to a beginner"
echo "  /ship             — automated ship workflow"
echo "  /review           — pre-landing code review"
echo ""
echo "See README.md for the full skill catalog and learning path."
