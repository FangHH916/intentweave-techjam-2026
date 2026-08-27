# Public Evaluation Results

## Aggregate metrics

| Agent | Hit Rate@10 | MRR | MTTC | Efficiency | TechnicalScore |
|---|---:|---:|---:|---:|---:|
| Official weak BM25 | 0.125 | 0.068034 | 9.810 | 0.1190 | 0.106710 |
| IntentWeave | **0.950** | **0.673812** | **2.780** | **0.8220** | **0.841544** |

Relative to the official starter, IntentWeave increases absolute Hit Rate@10 by
0.825 and reduces MTTC by 7.030 turns. Its TechnicalScore is approximately 7.89x
the baseline score.

## Scenario metrics

| Scenario | Sessions | Hit Rate@10 | MRR | MTTC |
|---|---:|---:|---:|---:|
| Buying | 80 | 0.9375 | 0.630441 | 2.4250 |
| Browsing | 80 | 0.9875 | 0.667927 | 2.4000 |
| Intent Override | 30 | 0.866667 | 0.800000 | 4.6000 |
| Boundary | 10 | 1.0000 | 0.689286 | 3.2000 |

## Reproduction

Environment used for the recorded run:

- Python 3.14.7, Windows
- Standard-library SQLite FTS5
- No network or external model
- Prompt tokens: 0
- Completion tokens: 0
- Wall time: 106.03 seconds on the development machine

Command:

```bash
python -m evaluator.local_evaluator --output results.json
```

The evaluator, public labels, scoring configuration, and catalog contents were
not modified. The catalog archive SHA256 was verified as:

```text
07fd142631fd6b03e2b4d09988c3eb7d53720e9d57010c79db48eeaada50a8f8
```

Public-set metrics are for development comparison only. The 800-session private
set remains unseen.
