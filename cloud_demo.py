from __future__ import annotations

import json
from pathlib import Path

from lotline.cloud_backend import FalkorDBCloudAgent
from lotline.models import AlertInput


def run() -> dict:
    agent = FalkorDBCloudAgent()
    connection = agent.ping()
    agent.seed_northstar()
    alert = AlertInput(
        alert_id="ALERT-001",
        ingredient_lot_id="ING-ALM-042",
        hazard="undeclared_allergen",
        severity="high",
        description="Possible undeclared almond contamination",
    )
    plan = agent.analyze(alert)
    expected = ["LOT-BITES-201", "LOT-GRANOLA-101", "LOT-GRANOLA-102"]
    if plan["affected_lots"] != expected:
        raise AssertionError(f"Unexpected affected set: {plan['affected_lots']}")
    if plan["safe_lots_spared"] != 7 or "LOT-GRANOLA-103" in plan["affected_lots"]:
        raise AssertionError("Cleaning/safe-lot invariant failed")
    approved = agent.approve(plan["case_id"], "OP-001")
    first = agent.execute(plan["case_id"])
    replay = agent.execute(plan["case_id"])
    if first["new_effects"] != 5 or replay["new_effects"] != 0:
        raise AssertionError("Idempotency invariant failed")
    return {
        "execution_status": "REAL — CLOUD",
        "connection": connection,
        "claim_scope": "Synthetic Northstar Foods fixture on a real FalkorDB Cloud graph.",
        "plan": plan,
        "approved_status": approved["status"],
        "first_execution": first,
        "replay_execution": replay,
        "final_case": agent.inspect(plan["case_id"]),
    }


if __name__ == "__main__":
    evidence = run()
    path = Path(__file__).parent / "evidence" / "cloud-demo-run.json"
    path.write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    print(json.dumps(evidence, indent=2))
    print(f"\nCloud evidence written to {path}")
