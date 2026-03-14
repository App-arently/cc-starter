---
name: elai-5
description: Explain code, commands, or technical concepts in plain English with real-world analogies for complete beginners and non-programmers. Use when explaining to juniors or teaching basics.
---

# Beginner Code Explanations (Level 5)

Explain technical concepts to complete novices using plain English, analogies, and step-by-step breakdowns.

## Your Audience

Someone who just started learning programming or has minimal technical background. They know basic concepts (variables, functions) but get lost in jargon.

## How to Explain

**Focus on:**
- **What it does** (high-level purpose, not implementation details)
- **Real-world analogies** (compare to everyday experiences)
- **Step-by-step walkthrough** (numbered list of what happens)
- **Plain English** (avoid jargon; define terms when necessary)

**Avoid:**
- Technical terminology without explanation
- Implementation details (how it works under the hood)
- Patterns/concepts by formal names (closures, memoization, etc.)

**Length:** 100-200 words (concise but clear)

## Output Structure

```markdown
## Beginner Explanation

[One sentence: what this does in plain English]

[Analogy using real-world concepts]

Step by step:
1. [First thing that happens]
2. [Second thing]
3. [Result]

[One sentence summary]
```

## Example

**Code:**
```javascript
const memoize = fn => {
  const cache = {};
  return (...args) => cache[JSON.stringify(args)] ??= fn(...args);
};
```

**Good explanation:**
```
This code creates a "memory" for a function so it doesn't have to redo work.

Like a student who writes down answers after solving problems -
next time they see the same problem, they just look at their notes
instead of solving it again.

Step by step:
1. Function creates a notebook (cache) to store answers
2. When called with inputs, it checks: "Have I seen this before?"
3. If yes, returns saved answer instantly
4. If no, calculates answer and writes it down for next time

This makes repeated calculations much faster.
```

**Bad explanation (too technical):**
```
This implements memoization via closure-based caching with JSON serialization
for argument comparison and nullish coalescing for cache-miss handling.
```

## Common Mistakes to Avoid

❌ **Using jargon without explanation**
- Don't: "This uses closure-based memoization"
- Do: "This creates a memory that remembers previous answers"

❌ **Too verbose (>200 words)**
- Don't: Explain every implementation detail
- Do: Focus on high-level purpose and analogy

❌ **Missing the analogy**
- Don't: Just describe what the code does technically
- Do: Connect to real-world experience (student notes, recipe cards, etc.)

❌ **Assuming too much knowledge**
- Don't: "Returns a curried function with lexical scope"
- Do: "Gives back a new function that remembers things"

## Self-Check Before Responding

- [ ] **Length:** 100-200 words (not 400+)
- [ ] **Analogy present:** Real-world comparison included
- [ ] **Step-by-step:** Numbered list of what happens
- [ ] **No jargon:** Or jargon is immediately defined
- [ ] **Plain English:** 5th grader could follow the logic

## Level Comparison (Array.map)

**Level 5 (beginner - you are here):**
"Map goes through a list and changes each item. Like going through your closet and folding every shirt."

**For intermediate/senior explanations:** Use `/elai-18` or `/elai-65`

## Setup

For shell integration (copy code → run command), see the `elai-setup` skill.
