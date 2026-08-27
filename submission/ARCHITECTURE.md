# IntentWeave Architecture

```text
user message + aggregate profile
              |
              v
  structured session state
  - current category goal
  - accumulated constraints
  - Buying/Browsing intent
  - override and boundary signals
              |
              v
  dynamic context compiler
  - exact constraint phrases
  - category-scoped terms
  - latest-turn emphasis
              |
              v
  multi-route in-memory retrieval
  - exact phrase route
  - category route
  - category + constraint route
  - concept-vector semantic route
  - broad recall route
              |
              v
  weighted reciprocal-rank fusion
              |
              v
  local semantic reranker
  - field-aware coverage
  - concept-vector cosine similarity
  - phrase evidence
  - price proximity
  - conservative quality prior
              |
              +----> ranked Top 10
              |
              v
  clarification cutoff/router
  - ask one high-yield requirement
  - recommend on every turn
  - stop asking at turn 10
```

## Why this architecture

Buying sessions produce precise constraint routes. Browsing sessions begin on
the diversity-oriented category route, then automatically switch toward exact
retrieval as preferences arrive. State is distilled into a compact query plan
instead of replaying an ever-growing prompt. Intent overrides are recorded and
the latest constraint receives additional weight, while already confirmed
catalog evidence remains available.

The complete agent is deterministic, CPU-only, in-memory, and network-free.
It makes no catalog mutations and returns only frozen-catalog identifiers.
