# IntentWeave

**An offline conversational shopping agent that compiles evolving intent into a
new retrieval plan on every turn.**

IntentWeave is a submission for TikTok TechJam 2026 Track 4, *Shopping Copilot:
AI Conversational Search and Recommendations*. It improves the official public
TechnicalScore from **0.106710** to **0.841544** while using no external API,
no foundation model, no network access, and no paid tokens.

## Public development results

| Agent | Hit Rate@10 | MRR | MTTC | Efficiency | TechnicalScore |
|---|---:|---:|---:|---:|---:|
| Official weak BM25 | 0.125 | 0.068034 | 9.81 | 0.1190 | 0.106710 |
| IntentWeave | **0.950** | **0.673812** | **2.780** | **0.8220** | **0.841544** |

These are deterministic results on the organizer's 200 labeled public sessions.
They are development results, not claims about the hidden 800-session set.
See [results and methodology](docs/RESULTS.md).

## What is different

- **Dual-track intent routing:** vague Browsing starts with category recall;
  Buying immediately activates high-precision constraint routes.
- **Dynamic context compilation:** the conversation becomes a compact goal plus
  constraints rather than an ever-growing prompt.
- **Multi-route hybrid retrieval:** exact phrases, categories,
  category-plus-constraint queries, a compact concept-vector semantic route,
  latest-turn evidence, and broad recall are fused with weighted reciprocal-rank
  fusion.
- **Local semantic reranking:** field-aware coverage, phrase evidence, price
  proximity, and a conservative quality prior reorder candidates.
- **Override-safe state:** abrupt intent changes are detected and latest evidence
  is emphasized without discarding confirmed catalog constraints.
- **Constraint-yield clarification:** while the pool is under-specified, the
  agent asks for the single remaining requirement most likely to reduce it and
  still recommends on every turn.

The architecture is described in [ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Requirements

- Python 3.10 or later
- Python built with SQLite FTS5 support (included in standard CPython builds)
- Approximately 200-500 MB free memory, depending on Python/SQLite version
- No network connection during inference

There are no third-party Python dependencies.

## Setup

Clone this repository, then download the organizer's frozen catalog:

```bash
curl -L -o data/catalog.jsonl.gz \
  https://github.com/TechJam2026/techjam-conversational-search/releases/download/participant-kit/catalog.jsonl.gz
```

Verify the catalog checksum against `data/SHA256SUMS`, then extract it:

```bash
gzip -dk data/catalog.jsonl.gz
```

The expected path is `data/catalog.jsonl`. The catalog is intentionally ignored
by Git and must not be committed.

## Reproduce the score

Run the unmodified official evaluator:

```bash
python -m evaluator.local_evaluator --output results.json
```

Run all tests:

```bash
python -m unittest discover -v
```

Trace one complete multi-turn session:

```bash
python -m scripts.trace_session public_0001
```

Build the standalone submission bundle:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_submission.ps1
```

The generated `submission/` directory contains the entry file, source package,
requirements, and reproduction instructions.

## Repository layout

```text
intentweave/                 production agent source
  agent.py                   official interface and orchestration
  state.py                   intent and multi-turn memory
  retrieval.py               lexical + concept-vector retrieval, fusion, reranking
starter/agent.py             official evaluator entry point
evaluator/                   organizer evaluator (unmodified)
data/public_set.jsonl        organizer public sessions (unmodified)
scripts/trace_session.py     deterministic demo/diagnostic
scripts/build_submission.ps1 standalone bundle builder
tests/                       evaluator and agent contract tests
docs/                        architecture, method, results, demo, Devpost copy
```

## Reproducibility and catalog integrity

- The catalog is opened read-only by the application and indexed into an
  in-memory SQLite database.
- Recommendations contain only `parent_asin` values read from that catalog.
- No secrets, user IDs, private labels, or external services are used.
- Token usage is reported as zero because the agent calls no language model.
- Route weights are fixed constants; inference is deterministic.

## Limitations

Common attributes such as “Imported” or “100% Cotton” may still identify many
catalog items. A small pinned offline embedding model could improve paraphrase
handling, but would increase startup cost and submission size. Public labels
were used for development evaluation, so hidden-set performance may differ.
See the fuller [method report](docs/METHOD_REPORT.md).

## Tools and attribution

Development used Python, SQLite FTS5, VS Code, and OpenAI Codex. No inference API
is used by the submitted agent. Data attribution and license information are in
[DATA_ATTRIBUTION.md](DATA_ATTRIBUTION.md).
