# Innovation: Context-to-Query Compilation

Most conversational search prototypes make the transcript longer on every turn
and ask an LLM to reinterpret it from scratch. IntentWeave instead treats the
conversation as a small program that is recompiled after every answer.

## The compiled context

```text
ConversationState = {
  goal,
  route: Buying | Browsing,
  active constraints,
  latest evidence,
  override count,
  rejected question facets
}
```

The compiler maps this state to multiple retrieval routes. Browsing activates a
wide category route. A hard constraint activates exact-phrase and
category-plus-constraint routes. New evidence receives a recency boost. An
override changes the routing mode immediately while preserving catalog evidence
that remains useful.

## Expected Constraint Yield

Clarification is an optimization decision, not a scripted questionnaire. The
agent asks while the candidate pool is saturated and the compact state contains
too little differentiating evidence. It requests one high-yield requirement
rather than cycling through color, brand, material, and price regardless of what
the shopper cares about. A ranked list is still returned on every turn, allowing
early conversion.

The practical objective is:

```text
question value = expected candidate reduction / one additional turn
```

This connects the innovation directly to MTTC. It is also lightweight: runtime
adaptation changes the query plan, not the model weights, so the complete system
remains deterministic, offline, and inexpensive.

## Why it matters beyond the challenge

The same compiler can add inventory, delivery, policy, and seller constraints as
new routes without retraining a foundation model. The state is inspectable for
debugging and compliance, while the retrieval plan is reproducible for each
recommendation.
