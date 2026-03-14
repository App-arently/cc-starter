---
name: killbloat
description: Trim bloat from skills - removes tool-how-tos, example transcripts, Claude-explanation. Keeps decisions, humanreadable workflow, rules. Target ~60 lines.
argument-hint: "{skill-name}"
allowed-tools: Read Edit Bash
---

# Workflow

1. **Read** `~/.claude/skills/{skill-name}/SKILL.md`
2. **Analyze** for bloat:
   - Tool mechanics (how to invoke AskUserQuestion, Bash, etc.)
   - Example transcripts (28-line "what it looks like" sections)
   - Obvious edge cases (skill not found, invalid syntax)
   - Repeated content (invocation shown 3+ times)
   - Output formatting instructions (Claude already knows)
   - Cost speculation without actionable routing
3. **Identify keep**:
   - Frontmatter (required)
   - Workflow (what decisions, compressed)
   - Rules (behavior constraints)
   - One minimal example (10 lines max)
   - 2-3 non-obvious edge cases
4. **Trim** following memory rules: explain decisions not mechanics, humanreadable not Claude-tutorial
5. **Show** before/after line count + what was removed
6. **Ask** confirm before writing

# Rules

- Never touch frontmatter (especially `argument-hint` - critical for UX)
- Preserve all workflow decision points
- Keep all rules section
- Compress but don't delete example (unless >20 lines, then trim to 10)
- Target ~60 lines, accept 50-70 range
- Show line diff before writing

# Example

```
/killbloat s2s

Read: 176 lines
Bloat found:
- Lines 8-10: repeats frontmatter
- Lines 53-57: Claude knows skill2prompt
- Lines 101-117: cost speculation + output formatting
- Lines 127-155: 28-line example transcript
- Lines 157-175: 4 obvious edge cases

Keep: frontmatter (6) + workflow (30) + rules (6) + example (10) + 2 edge cases (8) = 60 lines

Confirm trim? [y/n]
```
