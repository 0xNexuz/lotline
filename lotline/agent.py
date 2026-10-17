from __future__ import annotations

from .memory_graph import MemoryGraphStore
from .models import AlertInput


class LotLineAgent:
    """Safe, deterministic perceive-plan-approve-act agent."""

    def __init__(self, graph: MemoryGraphStore, cross_contact_window_minutes: int = 60) -> None:
        self.graph = graph
        self.cross_contact_window_minutes = cross_contact_window_minutes

    def analyze(self, alert: AlertInput) -> dict:
        self.graph.create_alert(alert)
        existing_case = self.graph.case_for_alert(alert.alert_id)
        if existing_case:
            return self.graph.case_snapshot(existing_case)

        direct = self.graph.direct_exposures(alert.alert_id)
        cross_contact = self.graph.cross_contact_exposures(
            alert.alert_id, self.cross_contact_window_minutes
        )

        # Safety policy v1: high-severity direct and uncleaned shared-line
        # exposures enter the recall set. Lower severity cases remain review-only.
        exposures = direct + cross_contact if alert.severity == "high" else direct
        case_id = self.graph.create_case(alert, exposures)
        snapshot = self.graph.case_snapshot(case_id)
        if alert.severity != "high" and cross_contact:
            snapshot["review_candidates"] = [item.lot_id for item in cross_contact]
        return snapshot

    def approve(self, case_id: str, operator_id: str) -> dict:
        return self.graph.approve_case(case_id, operator_id)

    def execute(self, case_id: str) -> dict:
        return self.graph.execute_case(case_id).to_dict()

    def inspect(self, case_id: str) -> dict:
        return self.graph.case_snapshot(case_id)
