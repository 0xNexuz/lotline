from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from lotline import LotLineAgent, MemoryGraphStore
from lotline.models import AlertInput


def _alert(alert_id: str, severity: str = "high") -> AlertInput:
    return AlertInput(
        alert_id=alert_id,
        ingredient_lot_id="ING-ALM-042",
        hazard="undeclared_allergen",
        severity=severity,
        description="Possible undeclared almond contamination",
    )


def _agent() -> tuple[MemoryGraphStore, LotLineAgent]:
    graph = MemoryGraphStore()
    graph.seed_northstar()
    return graph, LotLineAgent(graph)


def run_scenarios() -> dict[str, Any]:
    scenarios: list[dict[str, Any]] = []

    graph, agent = _agent()
    baseline = agent.analyze(_alert("ALERT-S01"))
    assert baseline["affected_lots"] == [
        "LOT-BITES-201",
        "LOT-GRANOLA-101",
        "LOT-GRANOLA-102",
    ]
    scenarios.append({
        "id": "S01",
        "name": "High-severity direct and shared-line exposure",
        "expected": "Two direct lots and one uncleaned adjacent lot require action.",
        "observed": {"affected_lots": baseline["affected_lots"], "safe_lots_spared": 7},
        "status": "VERIFIED",
    })

    graph, agent = _agent()
    medium = agent.analyze(_alert("ALERT-S02", "medium"))
    assert medium["affected_lots"] == ["LOT-GRANOLA-101", "LOT-GRANOLA-102"]
    assert medium["review_candidates"] == ["LOT-BITES-201"]
    scenarios.append({
        "id": "S02",
        "name": "Medium-severity adjacent exposure remains review-only",
        "expected": "Direct lots require action; the adjacent lot is surfaced for review.",
        "observed": {
            "affected_lots": medium["affected_lots"],
            "review_candidates": medium["review_candidates"],
        },
        "status": "VERIFIED",
    })

    graph, agent = _agent()
    graph.nodes["RUN-101"].properties["started_at"] = "2026-10-16T11:05:00Z"
    outside_window = agent.analyze(_alert("ALERT-S03"))
    assert outside_window["affected_lots"] == ["LOT-GRANOLA-101", "LOT-GRANOLA-102"]
    scenarios.append({
        "id": "S03",
        "name": "Adjacent run outside the 60-minute policy window",
        "expected": "The late adjacent lot is excluded.",
        "observed": {"affected_lots": outside_window["affected_lots"], "safe_lots_spared": 8},
        "status": "VERIFIED",
    })

    graph, agent = _agent()
    graph.nodes["CLEAN-01"].properties["validated"] = False
    unvalidated_cleaning = agent.analyze(_alert("ALERT-S04"))
    assert unvalidated_cleaning["affected_lots"] == [
        "LOT-BITES-201",
        "LOT-GRANOLA-101",
        "LOT-GRANOLA-102",
        "LOT-GRANOLA-103",
    ]
    scenarios.append({
        "id": "S04",
        "name": "Unvalidated cleaning cannot stop propagation",
        "expected": "Both adjacent runs inside the window remain exposed.",
        "observed": {"affected_lots": unvalidated_cleaning["affected_lots"], "safe_lots_spared": 6},
        "status": "VERIFIED",
    })

    graph, agent = _agent()
    graph.remove_edge("ING-ALM-042", "USED_IN", "RUN-100")
    disconnected = agent.analyze(_alert("ALERT-S05"))
    assert disconnected["decision"] == "CLEAR"
    assert disconnected["affected_lots"] == []
    assert disconnected["actions"] == []
    scenarios.append({
        "id": "S05",
        "name": "Missing load-bearing lineage edge",
        "expected": "No path means no proposed action.",
        "observed": {"decision": disconnected["decision"], "affected_lots": []},
        "status": "VERIFIED",
    })

    graph, agent = _agent()
    replay_case = agent.analyze(_alert("ALERT-S06"))
    blocked_before_approval = False
    try:
        agent.execute(replay_case["case_id"])
    except PermissionError:
        blocked_before_approval = True
    assert blocked_before_approval
    agent.approve(replay_case["case_id"], "OP-001")
    first = agent.execute(replay_case["case_id"])
    replay = agent.execute(replay_case["case_id"])
    assert first["new_effects"] == 5 and replay["new_effects"] == 0
    scenarios.append({
        "id": "S06",
        "name": "Approval gate and idempotent replay",
        "expected": "Pre-approval execution is blocked; replay creates no duplicate effect.",
        "observed": {
            "pre_approval_blocked": blocked_before_approval,
            "first_new_effects": first["new_effects"],
            "replay_new_effects": replay["new_effects"],
        },
        "status": "VERIFIED",
    })

    return {
        "execution_status": "MOCKED",
        "purpose": "Deterministic adversarial policy coverage; not FalkorDB Cloud execution.",
        "summary": {"scenario_count": len(scenarios), "verified": len(scenarios)},
        "scenarios": scenarios,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the LotLine safety scenario benchmark.")
    parser.add_argument("--write", action="store_true", help="Write evidence/scenario-benchmark.json")
    args = parser.parse_args()
    result = run_scenarios()
    if args.write:
        output = Path(__file__).parent / "evidence" / "scenario-benchmark.json"
        output.write_text(f"{json.dumps(result, indent=2)}\n", encoding="utf-8")
        print(f"scenario-benchmark: {result['summary']['verified']}/6 verified; wrote {output}")
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
