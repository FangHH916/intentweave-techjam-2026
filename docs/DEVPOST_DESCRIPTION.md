# IntentWeave — Devpost Description

## Inspiration

Traditional shopping search treats every message as a fresh keyword query. Real
shopping does not work that way: people begin vague, reveal constraints, reject
options, and sometimes change their minds. The challenge is not merely to
retrieve a relevant category—it is to convert an evolving conversation into the
right product with as little cognitive load as possible.

## What it does

IntentWeave is an offline conversational shopping agent that recompiles its
retrieval strategy on every turn. It routes vague Browsing requests toward broad
category discovery, switches Buying requests toward exact constraints, maintains
a compact structured session state, detects intent overrides, asks one high-yield
clarification question, and returns a ranked Top 10 on every turn.

Its innovation is **dynamic context compilation**: instead of repeatedly sending
the full transcript to a large model, it turns accumulated evidence into a small
runtime retrieval program. Exact phrases, category evidence, latest-turn context,
and broad recall execute as separate in-memory routes. A compact, auditable
concept vector handles common category, material, and use-case synonyms using
cosine similarity. Weighted reciprocal-rank fusion combines the routes, then a
local field-aware scorer reranks candidates using coverage, phrase evidence,
price proximity, and quality confidence.

## How we built it

- Python 3.10+ and dataclasses for the Agent and state machine
- SQLite FTS5 for the in-memory search index
- Standard-library scoring and weighted reciprocal-rank fusion
- The organizer's frozen 50,000-product Amazon Reviews 2023 catalog
- The official deterministic evaluator and 200 public development sessions
- VS Code and OpenAI Codex for development

No external inference API, vector database, foundation model, network connection,
or paid token is required.

## Results

On the official 200-session public development set:

- Hit Rate@10: **0.950** (starter: 0.125)
- MRR: **0.673812** (starter: 0.068034)
- MTTC: **2.780** (starter: 9.81)
- TechnicalScore: **0.841544** (starter: 0.106710)
- Token usage and estimated API cost: **0**

IntentWeave reaches 0.9875 Hit Rate@10 on Browsing sessions and 1.0 on Boundary
sessions. These are public development metrics; the private evaluation set is
unseen.

## Challenges

The hardest cases contain generic constraints such as “Imported” and “100%
Cotton,” shared by many products. We also had to balance early recommendations
against asking useful questions, handle override turns without accidentally
discarding still-valid evidence, and keep the complete pipeline portable under
unknown CPU, memory, and network restrictions.

## Accomplishments

We built a deterministic end-to-end Agent that uses the official interface,
indexes the full catalog in memory, handles all four scenario types, runs without
credentials, validates its output contract, and improves every core technical
metric by a large margin.

## What we learned

For this task, better context orchestration matters more than a larger model.
Separating recall routes and explicitly representing conversation state produced
larger, more reliable gains than treating the transcript as one search string.

## What's next

We would add a small pinned offline embedding model for freer paraphrases,
cross-validate route weights, and learn the clarification-value policy on
held-out sessions. In production, the same compact state could support inventory,
availability, and policy constraints without changing the catalog.
