from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from intentweave.agent import Agent
from intentweave.retrieval import concept_vector
from intentweave.state import SessionState, extract_signal


class StateTest(unittest.TestCase):
    def test_concept_vector_maps_use_case_synonyms(self) -> None:
        vector = concept_vector("Breathable sneakers for gym training")
        self.assertTrue({"footwear", "athletic", "lightweight"}.issubset(vector))

    def test_extracts_goal_and_accumulates_constraints(self) -> None:
        state = SessionState("s", {"preference_tags": ["comfort"]})
        state.update("I'm looking for Women Running Shoes, but I'm still exploring.")
        state.update("For that, what matters is: leather; color: black.")
        self.assertEqual(state.goal, "Women Running Shoes")
        self.assertEqual(state.constraints, ["leather", "color: black"])
        self.assertEqual(state.intent, "buying")

    def test_override_is_detected_without_erasing_valid_evidence(self) -> None:
        state = SessionState("s", {})
        state.update("I'm looking for Women Shoes. casual")
        state.update("Actually, ignore my earlier preference. What I need is: waterproof.")
        self.assertEqual(state.override_count, 1)
        self.assertEqual(state.intent, "buying")
        self.assertIn("waterproof", [item.lower() for item in state.constraints])

    def test_signal_removes_protocol_boilerplate(self) -> None:
        self.assertEqual(extract_signal("For that, what matters is: 100% Cotton."), "100% Cotton")


class AgentContractTest(unittest.TestCase):
    def test_offline_agent_returns_valid_contract_and_target(self) -> None:
        products = [
            {
                "parent_asin": "A",
                "title": "Blue cotton running shoe",
                "features": ["breathable cotton upper"],
                "details": {"Department": "Women"},
                "description": ["daily running"],
                "categories": ["Women", "Shoes", "Running"],
                "store": "Example",
                "price": 49.0,
                "average_rating": 4.5,
                "rating_number": 50,
            },
            {
                "parent_asin": "B",
                "title": "Black leather winter boot",
                "features": ["warm leather"],
                "details": {"Department": "Women"},
                "description": ["winter use"],
                "categories": ["Women", "Shoes", "Boots"],
                "store": "Example",
                "price": 89.0,
                "average_rating": 4.0,
                "rating_number": 10,
            },
        ]
        with tempfile.TemporaryDirectory() as directory:
            catalog = Path(directory) / "catalog.jsonl"
            catalog.write_text("".join(json.dumps(item) + "\n" for item in products), encoding="utf-8")
            agent = Agent(catalog)
            agent.reset("session", {"preference_tags": ["comfort"]})
            response = agent.respond(
                "session",
                "I'm looking for Women Running. A key requirement is: breathable cotton upper.",
                1,
                10,
            )
        self.assertEqual(response["recommendations"][0]["parent_asin"], "A")
        self.assertIn(response["ask_attribute"], {"feature", "other", None})
        self.assertEqual(response["usage"], {"prompt_tokens": 0, "completion_tokens": 0})


if __name__ == "__main__":
    unittest.main()
