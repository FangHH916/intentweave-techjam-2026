"""Trace one public session without changing the official evaluator."""

from __future__ import annotations

import argparse

from evaluator.local_evaluator import (
    catalog_index,
    coarse_category,
    customer_reply,
    initial_message,
    load_jsonl,
    materialize_hidden_fields,
)
from intentweave.agent import Agent


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("sample_id")
    parser.add_argument("--catalog", default="data/catalog.jsonl")
    parser.add_argument("--dataset", default="data/public_set.jsonl")
    args = parser.parse_args()

    samples = {sample["sample_id"]: sample for sample in load_jsonl(args.dataset)}
    sample = samples[args.sample_id]
    _, categories, products = catalog_index(args.catalog)
    target = str(sample["ground_truth"]["parent_asin"])
    card, behavior = materialize_hidden_fields(sample, products)
    effective = {**sample, "intent_card": card, "behavior": behavior}
    agent = Agent(args.catalog)
    agent.reset("trace", sample["user_profile"])
    disclosed: set[str] = set()
    boundary_used = False
    override_applied = sample["scenario_type"] != "intent_override"
    message = initial_message(effective, coarse_category(categories[target]), disclosed)
    print(f"target={target} title={products[target]['title']} card={card}")
    for turn in range(1, 11):
        response = agent.respond("trace", message, turn, 100)
        ranked = [item["parent_asin"] for item in response["recommendations"]]
        rank = ranked.index(target) + 1 if target in ranked else None
        print(f"turn={turn} user={message!r}")
        print(f"  ask={response['ask_attribute']} target_rank={rank} top3={ranked[:3]}")
        if override_applied and rank is not None:
            print(f"conversion: turn={turn} rank={rank}")
            break
        if turn == 10:
            break
        override = effective.get("behavior", {}).get("override") or {}
        if not override_applied and turn + 1 == int(override.get("turn", 3)):
            override_applied = True
            new_value = str(override.get("new_value", ""))
            if new_value:
                disclosed.add(new_value)
            message = str(override.get("message", "Actually, please ignore my earlier preference."))
        else:
            message, boundary_used = customer_reply(effective, response["ask_attribute"], disclosed, boundary_used)


if __name__ == "__main__":
    main()
