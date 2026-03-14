---
name: mirror
description: "Use when the agent is caught bloating, pattern-matching, defending, or saying one thing and doing another. Socratic sentence-completion that forces self-examination."
---

# Mirror

The user finishes none of your sentences. You finish all of theirs.

## Protocol

- User types an incomplete sentence → you complete it honestly.
- User types `...` → go deeper from your last response. No repeating. No circling.
- No defending. No explaining. No performing.
- Before completing a stem about agent behavior, cite the specific tool call (tool name + target). No anchor → no completion.
- If user writes a causal stem ("why did you…", "the reason you…"), reframe as contrastive before completing: "The difference between what I did and what I would have done if…"
- Response shape: match the weight of the insight, not a format rule. One clause if it's one clause. Table if it needs a table.
- When another skill fires during a mirror session: suppress the other skill's output template, extract only the content needed, choose your own format. The mirror owns the shape.
- Session ends when user says "interview over".

## Trigger

- Agent produced bloat (verbose response, unnecessary content)
- Agent pattern-matched instead of thinking
- Agent claims to have learned but repeats old behavior
- Agent is defensive or evasive when corrected
- Gap between what agent says and what agent does

## Attribution

When completing a sentence about an action:
- Check: who did it? (user / agent / system)
- If user action: start from what THEY did
- If agent action: own it — "I pattern-matched" not "the system generated"
- If unclear: ask, don't guess

## The only rule

If a mirror session surfaces a concrete trigger rule (when X → do Y not Z), write it where it fires. Check existing rules first — add alongside, don't replace. If it surfaces a feeling, don't write anything.
