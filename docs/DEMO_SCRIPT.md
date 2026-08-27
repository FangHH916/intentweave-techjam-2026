# Three-Minute Demo Script

## 0:00-0:30 — Problem

“The starter searches only the current message. It scores 0.125 Hit Rate@10 and
usually needs almost all ten turns. Shopping intent, however, evolves.”

Show `docs/baseline_results.json`.

## 0:30-1:30 — End-to-end session

Run:

```bash
python -m scripts.trace_session public_0001
```

Point out the category goal, the proactive question, constraint accumulation,
and the target moving to rank one.

## 1:30-2:05 — Intent override

Run:

```bash
python -m scripts.trace_session public_0003
```

Explain that IntentWeave detects the override, emphasizes the new constraint,
and recompiles the retrieval routes without replaying a large prompt.

## 2:05-2:35 — Architecture

Show `docs/ARCHITECTURE.md`. Explain multi-route retrieval, weighted fusion, and
local reranking. Emphasize that the system is offline and catalog-safe.

## 2:35-3:00 — Results and impact

Show `docs/RESULTS.md` and close with:

“IntentWeave spends zero tokens and zero API dollars. It turns each answer into a
better retrieval program, reaching the purchased product earlier and making the
architecture practical beyond the hackathon.”
