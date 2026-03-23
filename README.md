# cc-starter

A curated starter kit for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) — battle-tested skills, a CLAUDE.md template, and safety hooks to shortcut the learning curve. Clone it, run the installer, and start using workflows that took months to develop.

## Quick Start

```bash
git clone https://github.com/App-arently/cc-starter.git
cd cc-starter
./install.sh
```

The installer:
- Symlinks skills into `~/.claude/skills/` (your existing skills are never overwritten)
- Copies `CLAUDE.md.template` to `~/.claude/CLAUDE.md` (only if you don't have one yet)
- Installs safety hooks and shows you how to enable them
- Initializes meta-team memory for the team orchestration skill

## Skill Catalog

| Skill | What it does | When to use it | Invoke |
|-------|-------------|----------------|--------|
| **brainstorming** | Collaborative design exploration — asks questions one at a time, proposes approaches, presents design in sections | Before any creative work: features, components, architecture | `/brainstorming` |
| **elai-5** | Explains code in plain English with real-world analogies | Teaching beginners, explaining to non-programmers | `/elai-5` |
| **elai-18** | Explains code with patterns, working examples, and best practices | Developers with 1-2 years experience learning patterns | `/elai-18` |
| **elai-65** | Explains architecture, trade-offs, edge cases, and production concerns | Senior developers making design decisions | `/elai-65` |
| **mirror** | Socratic sentence-completion that forces self-examination | When Claude is bloating, pattern-matching, or defending | `/mirror` |
| **killbloat** | Trims bloat from skills — removes tool-how-tos, example transcripts | After writing or editing a skill | `/killbloat <skill-name>` |
| **review** | Pre-landing code review — SQL safety, trust boundaries, structural issues | Before merging a PR | `/review` |
| **ship** | Full ship workflow — merge, test, review, version bump, changelog, PR | When ready to ship a feature branch | `/ship` |
| **qa** | Systematic QA testing — diff-aware, full, quick, regression modes | After deploying or when dogfooding | `/qa` |
| **knowledge-cache** | Library cheatsheets with preferred patterns and pitfalls | When coding with cached libraries, or adding a new cheatsheet | `/knowledge-cache add <lib>` |
| **meta-team** | Decompose intent and orchestrate Claude Code agent teams | Complex multi-deliverable tasks needing parallel agents | `/meta-team <objective>` |

## Learning Path

### Day 1: Foundations

1. **Read `CLAUDE.md`** — understand the rules Claude follows in your projects
2. **Try `/brainstorming`** — before building anything, explore the idea first
3. **Try `/elai-5`** or **`/elai-18`** — paste code you don't understand, get an explanation at your level

### Week 1: Core Workflows

4. **`/review`** — run it before every PR. Catches SQL injection, trust boundary violations, and structural issues that tests miss
5. **`/ship`** — automates the entire ship workflow: merge main, run tests, review, bump version, changelog, commit, push, PR
6. **`/mirror`** — when Claude gives you a wall of text or keeps defending a bad approach, use this to force self-examination

### Week 2+: Power Tools

7. **`/meta-team`** — for large tasks, decomposes your intent and spawns a coordinated agent team with failure mode mitigations
8. **`/qa`** — systematic QA testing with health scores, screenshots, and regression tracking
9. **`/knowledge-cache`** — build up a library of cheatsheets so Claude always uses your preferred patterns

## How Hooks Work

Hooks are shell scripts that run before Claude executes certain tools. They act as safety gates — if a hook exits with code 2, the tool call is blocked.

This starter includes two example hooks:

- **`gate-agent.sh`** — Enforces `isolation: "worktree"` when spawning agents that edit files. Prevents broken imports and commit races from parallel agents sharing a working tree.
- **`gate-bash.sh`** — Blocks obviously dangerous commands: `rm -rf /`, `chmod 777`, `git push --force main`, etc.

To enable them, merge `settings-hooks.json` into your `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Agent",
        "hooks": [{ "type": "command", "command": "~/.claude/skills/hooks/gate-agent.sh" }]
      },
      {
        "matcher": "Bash",
        "hooks": [{ "type": "command", "command": "~/.claude/skills/hooks/gate-bash.sh" }]
      }
    ]
  }
}
```

## Adding Your Own Skills

Create a directory in `~/.claude/skills/` with a `SKILL.md` file:

```
~/.claude/skills/my-skill/
└── SKILL.md
```

The `SKILL.md` needs YAML frontmatter with at least `name` and `description`:

```yaml
---
name: my-skill
description: "What this skill does — Claude uses this to decide when to activate it"
---

# My Skill

Instructions for Claude when this skill is invoked...
```

Invoke with `/my-skill` in Claude Code.

**Tips:**
- Keep skills focused — one skill, one job
- Use `/killbloat` after writing a skill to trim unnecessary content
- Use `/mirror` if your skill's output is bloated or repetitive
- Reference files with relative paths from `~/.claude/skills/` so they work after symlink

## Resources

- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code)
- [Claude Code GitHub](https://github.com/anthropics/claude-code)
- [CLAUDE.md Guide](https://docs.anthropic.com/en/docs/claude-code/memory)
- [Hooks Documentation](https://docs.anthropic.com/en/docs/claude-code/hooks)

## License

MIT

## Contact

Built by **Youssef Hajar** — [yhajar@biedkracht.nl](mailto:yhajar@biedkracht.nl)
