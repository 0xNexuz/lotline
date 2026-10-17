from __future__ import annotations

import unittest

from lotline import LotLineAgent, MemoryGraphStore
from lotline.models import AlertInput


def alert() -> AlertInput:
    return AlertInput(
        alert_id="ALERT-001",
        ingredient_lot_id="ING-ALM-042",
        hazard="undeclared_allergen",
        severity="high",
        description="Possible undeclared almond contamination",
    )


class LotLineProofTests(unittest.TestCase):
    def setUp(self) -> None:
        self.graph = MemoryGraphStore()
        self.graph.seed_northstar()
        self.agent = LotLineAgent(self.graph)

    def test_expected_recall_set_and_safe_lots(self) -> None:
        plan = self.agent.analyze(alert())
        self.assertEqual(
            plan["affected_lots"],
            ["LOT-BITES-201", "LOT-GRANOLA-101", "LOT-GRANOLA-102"],
        )
        self.assertEqual(plan["affected_lot_count"], 3)
        self.assertEqual(plan["safe_lots_spared"], 7)
        self.assertEqual(plan["locations"], ["STORE-NORTH", "STORE-SOUTH"])

    def test_validated_cleaning_excludes_later_run(self) -> None:
        plan = self.agent.analyze(alert())
        self.assertNotIn("LOT-GRANOLA-103", plan["affected_lots"])

    def test_actions_require_approval(self) -> None:
        plan = self.agent.analyze(alert())
        with self.assertRaises(PermissionError):
            self.agent.execute(plan["case_id"])

    def test_execution_is_idempotent(self) -> None:
        plan = self.agent.analyze(alert())
        self.agent.approve(plan["case_id"], "OP-001")
        first = self.agent.execute(plan["case_id"])
        replay = self.agent.execute(plan["case_id"])
        self.assertEqual(first["new_effects"], 5)
        self.assertEqual(first["existing_effects"], 0)
        self.assertEqual(replay["new_effects"], 0)
        self.assertEqual(replay["existing_effects"], 5)

    def test_graph_edge_is_load_bearing(self) -> None:
        self.graph.create_alert(alert())
        before = self.graph.direct_exposures("ALERT-001")
        self.graph.remove_edge("ING-ALM-042", "USED_IN", "RUN-100")
        after = self.graph.direct_exposures("ALERT-001")
        self.assertEqual({item.lot_id for item in before}, {"LOT-GRANOLA-101", "LOT-GRANOLA-102"})
        self.assertEqual(after, [])

    def test_every_quarantine_has_evidence(self) -> None:
        plan = self.agent.analyze(alert())
        evidence_ids = {item["id"] for item in plan["evidence"]}
        quarantine_actions = [a for a in plan["actions"] if a["action_type"] == "QUARANTINE"]
        self.assertEqual(len(quarantine_actions), 3)
        for action in quarantine_actions:
            action_id = action["id"]
            linked = self.graph._targets(action_id, "SUPPORTED_BY")
            self.assertEqual(len(linked), 1)
            self.assertIn(linked[0], evidence_ids)


if __name__ == "__main__":
    unittest.main()
