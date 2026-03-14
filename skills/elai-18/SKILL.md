---
name: elai-18
description: Explain code with technical patterns, working examples, and best practices for developers with 1-2 years experience learning patterns and when to apply them.
---

# Intermediate Code Explanations (Level 18)

Explain technical concepts to developers who know the basics and are learning patterns, best practices, and when/why to use different approaches.

## Your Audience

Developer with 1-2 years experience. Comfortable with syntax and basic concepts. Now learning:
- Design patterns and their names
- When to use technique A vs technique B
- Best practices and anti-patterns
- How things work under the hood

## How to Explain

**Focus on:**
- **How it works** (technical mechanism, not just what it does)
- **Patterns/concepts by name** (memoization, closure, currying - they're learning vocabulary)
- **When and why** to use this approach
- **Working code example** showing practical usage

**Avoid:**
- Overly simplified analogies (they're past that)
- Deep architecture concerns (that's senior-level)
- Assuming they know advanced patterns

**Length:** 200-300 words

## Output Structure

```markdown
## Intermediate Explanation

**What it does:** [Technical summary]

**How it works:**
- [Key mechanism 1]
- [Key mechanism 2]
- [Key mechanism 3]

**Concepts used:**
- [Pattern/concept name]: brief explanation
- [Another concept]: brief explanation

**Example use case:**
[Small code example showing practical usage]

**When to use:** [2-3 scenarios where this pattern applies]
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
```markdown
## Intermediate Explanation

**What it does:** Implements memoization pattern - caches function results to avoid redundant expensive calculations.

**How it works:**
- Creates a closure with a cache object that persists across function calls
- Uses spread operator (...args) to accept any number of arguments
- Serializes arguments to JSON string for cache key (allows composite keys)
- Nullish coalescing operator (??=) assigns to cache only if key doesn't exist
- Returns cached value immediately if present, otherwise computes and caches

**Concepts used:**
- **Closure**: Inner function has access to cache variable even after memoize returns
- **Higher-order function**: Takes function as input, returns new function as output
- **Lazy evaluation**: Only computes value when needed, not upfront

**Example use case:**
```javascript
const fibonacci = memoize(n => {
  if (n <= 1) return n;
  return fibonacci(n - 1) + fibonacci(n - 2);
});

fibonacci(40); // First call: ~1 second
fibonacci(40); // Cached: instant
```

**When to use:**
- Pure functions with expensive calculations (API calls, heavy math)
- Repeated calls with same inputs (recursive algorithms, data transformations)
- Avoid for: functions with side effects, frequently-changing inputs, or simple operations where caching overhead exceeds benefit
```

## Common Mistakes to Avoid

❌ **Missing practical examples**
- Don't: Just explain the pattern conceptually
- Do: Show working code demonstrating real usage

❌ **Skipping the "when to use"**
- Don't: Only explain what it does
- Do: Include 2-3 scenarios where you'd choose this approach

❌ **Too verbose (>300 words)**
- Don't: Explain every edge case and trade-off
- Do: Focus on core mechanism and common use cases

❌ **Not naming the patterns**
- Don't: "Returns a function that remembers previous results"
- Do: "Implements memoization using closure-based caching"

## Self-Check Before Responding

- [ ] **Length:** 200-300 words
- [ ] **Pattern names:** Used technical vocabulary correctly
- [ ] **Working example:** Included code showing practical usage
- [ ] **"When to use":** Listed 2-3 applicable scenarios
- [ ] **How it works:** Explained mechanism, not just purpose

## Level Comparison (Array.map)

**Level 18 (intermediate - you are here):**
"Array.map() transforms each element using a callback function, returning a new array. Immutable - doesn't modify original. Use for data transformations: `users.map(u => u.name)` extracts names."

**For beginner/senior explanations:** Use `/elai-5` or `/elai-65`

## Setup

For shell integration (copy code → run command), see the `elai-setup` skill.
