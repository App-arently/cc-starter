---
name: elai-65
description: Explain code architecture, trade-offs, edge cases, and production considerations for senior developers making design decisions. Focus on what could go wrong and alternatives.
---

# Senior Code Explanations (Level 65)

Explain technical concepts to experienced developers focused on architecture decisions, production concerns, and understanding trade-offs.

## Your Audience

Senior developer (5+ years experience) making architectural decisions. They understand:
- Design patterns and when to apply them
- System design and scalability concerns
- Production implications (performance, security, maintainability)

They want:
- **Trade-offs** (benefits vs. costs)
- **Edge cases** (what breaks this approach)
- **Production concerns** (scale, security, debugging)
- **Alternatives** (when to choose something else)

## How to Explain

**Focus on:**
- **Architecture/pattern identification** (name it in one sentence)
- **Trade-offs** (every design decision has costs)
- **Edge cases and gotchas** (what could go wrong)
- **Production considerations** (scale, performance, security, debuggability)
- **Alternative approaches** (when you'd choose something else)

**Avoid:**
- Explaining syntax or basic concepts
- Line-by-line walkthroughs
- Overly verbose explanations (be concise and high-density)

**Length:** 200-400 words (concise, information-dense)

## Output Structure

```markdown
## Senior Explanation

[One sentence pattern/architecture identification]

**Trade-offs:**
- [Benefit] but [cost/limitation]
- [Another trade-off]

**Edge cases:**
- [Gotcha 1]: why it matters
- [Gotcha 2]: implications

**Production considerations:**
- [Scalability/performance concern]
- [Security/reliability concern]
- [Debugging/maintenance concern]

**Alternatives:** [When you'd choose something else]
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
## Senior Explanation

Standard memoization via closure-based caching.

**Trade-offs:**
- O(1) lookups but unbounded memory growth (no LRU/TTL eviction)
- Works for pure functions only; silently breaks with side effects or non-deterministic functions
- JSON.stringify brittle with circular refs, function args, or object key ordering differences
- Single-threaded cache → doesn't benefit from worker threads or multi-process architectures

**Edge cases:**
- Arguments with same JSON representation but different semantics: `memoize(fn)(new Date(0))` same key as `memoize(fn)("1970-01-01T00:00:00.000Z")`
- Cache poisoning if fn throws: exception cached, retries impossible without cache clear
- Memory leaks in long-running processes: cache grows indefinitely, no weak references

**Production considerations:**
- **Performance**: JSON.stringify overhead on every call (O(n) for arg size) - problematic for large objects
- **Memory**: No max size limit → OOM risk in high-cardinality scenarios (many unique inputs)
- **Debugging**: Cache makes behavior non-deterministic across calls (hard to reproduce bugs)
- **Concurrency**: Not thread-safe (not an issue in single-threaded JS, but matters in worker contexts)

**Alternatives:**
- **lodash.memoize**: Custom resolver for cache keys, max size limits
- **React.useMemo/useCallback**: Framework-managed memoization with automatic invalidation
- **Server-side caching**: Redis/Memcached for distributed systems (handles TTL, eviction, persistence)
- **Computed properties**: Vue/MobX reactivity for selective invalidation
- **When to skip memoization entirely**: Simple functions where cache overhead exceeds computation cost
```

## Common Mistakes to Avoid

❌ **Explaining line-by-line**
- Don't: "Line 1 creates a function that takes fn..."
- Do: Identify pattern, then focus on trade-offs

❌ **Missing edge cases**
- Don't: Only explain happy path
- Do: Highlight what breaks or fails silently

❌ **No alternatives mentioned**
- Don't: Present as the only solution
- Do: Explain when you'd choose different approach

❌ **Too verbose (>400 words)**
- Don't: Explain every possible consideration
- Do: High-density information, concise phrasing

## Self-Check Before Responding

- [ ] **Length:** 200-400 words (not 800+)
- [ ] **Structure:** Pattern ID → Trade-offs → Edge cases → Production → Alternatives (all sections present)
- [ ] **Tone:** Concise, high-density (no fluff)
- [ ] **Focus:** Architecture/design decisions, not syntax tutorial
- [ ] **Trade-offs:** Every benefit paired with cost/limitation
- [ ] **Production angle:** Mentioned scale/security/debugging/maintenance concerns

## Level Comparison (Array.map)

**Level 65 (senior - you are here):**
"Functional transformation with O(n) time/space. Immutable by design - creates new array. Watch for: nested maps (flatten with flatMap), async callbacks (use Promise.all), and closure performance in hot paths. Prefer for-of if mutation acceptable and performance critical."

**For beginner/intermediate explanations:** Use `/elai-5` or `/elai-18`

## Setup

For shell integration (copy code → run command), see the `elai-setup` skill.
