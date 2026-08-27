# IntentWeave Standalone Submission

## Requirements

- Python 3.10+
- Standard-library SQLite with FTS5
- No third-party dependencies, API keys, model downloads, or network access

## Agent entry

`submission/agent.py` exports the required `Agent` class. The default constructor
expects the frozen catalog at `data/catalog.jsonl`; the official harness may also
pass an explicit catalog path.

From the repository root, verify the official integration with:

```bash
python -m evaluator.local_evaluator --output results.json
```

The public development result recorded for this build is TechnicalScore 0.841544,
Hit Rate@10 0.950, MRR 0.673812, and MTTC 2.780. Token usage and API cost are zero.

See `METHOD_REPORT.md` for architecture, model disclosure, and limitations.
