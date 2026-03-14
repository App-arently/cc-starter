---
name: knowledge-cache
description: Use when writing code involving cached libraries. Provides curated cheatsheets with preferred patterns, common pitfalls, and key idioms. Also use to add new library cheatsheets via "/knowledge-cache add <library>".
argument-hint: add <library-name>
user-invocable: true
---

# Knowledge Cache

Curated library cheatsheets. Read matching quick-ref.md before generating code for any detected library.

## Detected Project Dependencies

### Node.js / Frontend
!`cat package.json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(' '.join(sorted(set(list(d.get('dependencies',{}).keys()) + list(d.get('devDependencies',{}).keys())))))" 2>/dev/null`

### Python / Backend
!`cat requirements.txt 2>/dev/null | grep -v '^#' | grep -v '^$' | sed 's/[>=<].*//' | tr '\n' ' ' 2>/dev/null`
!`python3 -c "import tomllib; d=tomllib.load(open('pyproject.toml','rb')); print(' '.join(d.get('project',{}).get('dependencies',[])))" 2>/dev/null`

## Installed Cheatsheets

| Library | Path |
|---------|------|
!`for dir in ~/.claude/skills/knowledge-cache/*/; do lib=$(basename "$dir"); if [ -f "$dir/quick-ref.md" ]; then name=$(head -1 "$dir/quick-ref.md" | sed 's/^# //;s/ Quick Reference//'); echo "| $name | ${lib}/quick-ref.md |"; fi; done`

## Instructions

When detected dependencies match an installed cheatsheet:
1. Read the matching quick-ref.md file(s) before writing code for that library
2. Follow "Do This" patterns; avoid "Not That" anti-patterns
3. Apply version-specific notes

When multiple libraries match, read ALL matching cheatsheets.

---

## `add` Command

**Usage:** `/knowledge-cache add <library-name>`

Generates a new cheatsheet for any library and installs it.

### Steps

1. **Parse argument.** Extract library name. Normalize to lowercase kebab-case directory name.
   - Example: "React" → `react`, "Tailwind CSS" → `tailwindcss`, "SQLAlchemy" → `sqlalchemy`

2. **Check if already exists:**
   ```
   ls ~/.claude/skills/knowledge-cache/{lib}/quick-ref.md
   ```
   If exists: tell the user it's already installed. Offer to overwrite or stop.

3. **Generate the cheatsheet** following this exact template:

   ```markdown
   # {Library Display Name} Quick Reference
   > Version: {version}+ | Last updated: {YYYY-MM}

   ## Do This, Not That

   | Do This | Not That | Why |
   |---------|----------|-----|
   | {4-6 rows of concrete patterns} |

   ## Key Patterns

   ### {Pattern 1 Name}
   ```{lang}
   {3-8 lines of minimal, working code}
   ```

   ### {Pattern 2 Name}
   ```{lang}
   {3-8 lines of minimal, working code}
   ```

   ## Pitfalls

   - **{Pitfall 1}**: {what goes wrong} -- {fix}
   - **{Pitfall 2}**: {what goes wrong} -- {fix}
   - **{Pitfall 3}**: {what goes wrong} -- {fix}

   ## Version Notes

   - {version}+: {behavioral change agents should know about}
   ```

   **Quality rules:**
   - Target 200-400 tokens (150-350 words)
   - Every "Do This" must have a concrete "Not That" — no generic advice
   - Code snippets must be copy-pasteable — no pseudocode, no `...` placeholders
   - Pitfalls must describe what ACTUALLY goes wrong, not theoretical risks
   - Version notes only for breaking changes or major API shifts agents commonly miss
   - Use the LATEST stable version as baseline

4. **Write the file:**
   ```
   mkdir -p ~/.claude/skills/knowledge-cache/{lib}/
   ```
   Then write to `~/.claude/skills/knowledge-cache/{lib}/quick-ref.md`

5. **Confirm:** Tell the user the cheatsheet is installed and will auto-activate when the library is detected in projects.
