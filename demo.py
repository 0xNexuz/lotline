from __future__ import annotations

import json
from pathlib import Path

from lotline import LotLineAgent, MemoryGraphStore
from lotline.models import AlertInput


def run_demo() -> dict:
    graph = MemoryGraphStore()
    graph.seed_northstar()
    agent = LotLineAgent(graph)
    alert = AlertInput(
        alert_id="ALERT-001",
        ingredient_lot_id="ING-ALM-042",
        hazard="undeclared_allergen",
        severity="high",
        description="Possible undeclared almond contamination",
    )
    plan = agent.analyze(alert)
    approved = agent.approve(plan["case_id"], "OP-001")
    first_execution = agent.execute(plan["case_id"])
    replay_execution = agent.execute(plan["case_id"])
    return {
        "execution_status": "MOCKED",
        "claim_scope": "Synthetic Northstar Foods fixture; not production food-safety validation.",
        "plan": plan,
        "approved_status": approved["status"],
        "first_execution": first_execution,
        "replay_execution": replay_execution,
        "final_case": agent.inspect(plan["case_id"]),
    }


if __name__ == "__main__":
    evidence = run_demo()
    evidence_path = Path(__file__).parent / "evidence" / "demo-run.json"
    evidence_path.write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    print(json.dumps(evidence, indent=2))
    print(f"\nEvidence written to {evidence_path}")
