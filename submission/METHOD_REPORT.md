# IntentWeave Method Report

## Summary

IntentWeave is an offline conversational shopping agent designed to find the
hidden purchased product early and rank it highly. Its core insight is that a
conversation should compile into a new retrieval plan on every turn. A vague
Browsing turn uses category-level recall; each disclosed requirement adds an
exact or field-aware retrieval route; a Buying turn immediately prioritizes
hard evidence.

## Components

1. **Intent and state:** a deterministic state machine tracks category goal,
   accumulated constraints, Buying/Browsing transitions, boundary replies, and
   explicit intent overrides.
2. **Hybrid retrieval:** SQLite FTS5 executes exact-phrase, category,
   category-plus-constraint, compact concept-vector, latest-turn, and broad-recall
   routes entirely in memory. The concept route maps catalog language into an
   auditable apparel concept space and uses cosine similarity, avoiding model
   downloads while still handling common synonyms and use-case language.
3. **Fusion and reranking:** weighted reciprocal-rank fusion is followed by a
   local field-aware reranker using token coverage, exact phrase evidence,
   price proximity, and a small rating-confidence prior.
4. **Clarification routing:** the agent recommends on every turn and asks for
   one remaining high-yield requirement. It never exceeds the protocol's turn
   limit.

## Model, API, latency, and cost disclosure

- Foundation model: none.
- External API: none.
- Network required during official scoring: no.
- Prompt/completion tokens: 0 / 0.
- Estimated inference cost: USD 0.
- Runtime: Python 3.10+ standard library and SQLite FTS5.
- Public evaluation wall time: recorded in `docs/RESULTS.md` for the development
  machine; organizer hardware may differ.

## Dataset

The solution uses only the organizer's frozen 50,000-product catalog and 200
public development sessions derived from Amazon Reviews 2023,
`Clothing_Shoes_and_Jewelry`. The catalog is read-only. No mock products or ASINs
are added.

## Limitations

- The compact lexical semantic layer does not fully understand novel paraphrases
  as well as a pretrained embedding or cross-encoder model could.
- Very common attributes such as `Imported` or `100% Cotton` may leave many
  indistinguishable products.
- The public simulator provides controlled text; real shoppers would require
  stronger negation, typo, and free-form intent handling.
- Aggregate profile tags are intentionally treated conservatively because they
  may describe prior behavior rather than the current purchase.

## Next steps

Given more time, we would add a small, pinned, offline sentence-embedding model,
calibrate route weights with cross-validation rather than a single public split,
and learn the clarification value function from held-out sessions.
