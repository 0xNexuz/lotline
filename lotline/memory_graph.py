from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from typing import Any, Iterable

from .models import ActionResult, AlertInput, EvidencePath, Exposure


@dataclass
class Node:
    node_id: str
    label: str
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Edge:
    source: str
    relationship: str
    target: str


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


class MemoryGraphStore:
    """Deterministic graph test adapter.

    This adapter executes the same relationship semantics as the FalkorDB queries,
    but it is not FalkorDB. It exists so correctness and agent behavior can be run
    on machines without a FalkorDB runtime. Submission claims must label it MOCKED.
    """

    runtime_status = "MOCKED"

    def __init__(self) -> None:
        self.nodes: dict[str, Node] = {}
        self.outgoing: dict[str, list[Edge]] = defaultdict(list)
        self.incoming: dict[str, list[Edge]] = defaultdict(list)
        self.completed_effects: dict[str, dict[str, Any]] = {}

    def add_node(self, node_id: str, label: str, **properties: Any) -> None:
        self.nodes[node_id] = Node(node_id, label, {"id": node_id, **properties})

    def add_edge(self, source: str, relationship: str, target: str) -> None:
        if source not in self.nodes or target not in self.nodes:
            raise KeyError(f"Cannot connect missing nodes: {source} -> {target}")
        edge = Edge(source, relationship, target)
        if edge not in self.outgoing[source]:
            self.outgoing[source].append(edge)
            self.incoming[target].append(edge)

    def remove_edge(self, source: str, relationship: str, target: str) -> None:
        edge = Edge(source, relationship, target)
        if edge in self.outgoing[source]:
            self.outgoing[source].remove(edge)
        if edge in self.incoming[target]:
            self.incoming[target].remove(edge)

    def _targets(self, source: str, relationship: str) -> list[str]:
        return [edge.target for edge in self.outgoing[source] if edge.relationship == relationship]

    def _sources(self, target: str, relationship: str) -> list[str]:
        return [edge.source for edge in self.incoming[target] if edge.relationship == relationship]

    def seed_northstar(self) -> None:
        self.__init__()
        self.add_node("SUP-01", "Supplier", name="Almond Cooperative")
        self.add_node("ING-ALM-042", "IngredientLot", ingredient="almond meal")
        self.add_node("ING-ALM-043", "IngredientLot", ingredient="almond meal")
        self.add_edge("SUP-01", "PRODUCED", "ING-ALM-042")
        self.add_edge("SUP-01", "PRODUCED", "ING-ALM-043")

        self.add_node("LINE-01", "Line", name="Line 1")
        self.add_node("LINE-02", "Line", name="Line 2")
        self.add_node("RUN-100", "ProductionRun", started_at="2026-10-16T09:00:00Z", ended_at="2026-10-16T10:00:00Z")
        self.add_node("RUN-101", "ProductionRun", started_at="2026-10-16T10:05:00Z", ended_at="2026-10-16T10:15:00Z")
        self.add_node("RUN-102", "ProductionRun", started_at="2026-10-16T10:30:00Z", ended_at="2026-10-16T11:00:00Z")
        self.add_node("RUN-200", "ProductionRun", started_at="2026-10-16T11:10:00Z", ended_at="2026-10-16T12:30:00Z")
        self.add_edge("ING-ALM-042", "USED_IN", "RUN-100")
        self.add_edge("ING-ALM-043", "USED_IN", "RUN-200")
        self.add_edge("RUN-100", "RAN_ON", "LINE-01")
        self.add_edge("RUN-101", "RAN_ON", "LINE-01")
        self.add_edge("RUN-102", "RAN_ON", "LINE-01")
        self.add_edge("RUN-200", "RAN_ON", "LINE-02")

        self.add_node("CLEAN-01", "CleaningEvent", occurred_at="2026-10-16T10:20:00Z", validated=True)
        self.add_edge("LINE-01", "HAD_CLEANING", "CLEAN-01")

        lots = {
            "LOT-GRANOLA-101": ("GRANOLA-ALMOND", "RUN-100"),
            "LOT-GRANOLA-102": ("GRANOLA-ALMOND", "RUN-100"),
            "LOT-BITES-201": ("ENERGY-BITES", "RUN-101"),
            "LOT-GRANOLA-103": ("GRANOLA-ALMOND", "RUN-102"),
            "LOT-GRANOLA-104": ("GRANOLA-ALMOND", "RUN-200"),
            "LOT-GRANOLA-105": ("GRANOLA-ALMOND", "RUN-200"),
            "LOT-GRANOLA-106": ("GRANOLA-ALMOND", "RUN-200"),
            "LOT-GRANOLA-107": ("GRANOLA-ALMOND", "RUN-200"),
            "LOT-GRANOLA-108": ("GRANOLA-ALMOND", "RUN-200"),
            "LOT-GRANOLA-109": ("GRANOLA-ALMOND", "RUN-200"),
        }
        for lot_id, (sku, run_id) in lots.items():
            self.add_node(lot_id, "ProductLot", sku=sku, status="AVAILABLE")
            self.add_edge(run_id, "CREATED", lot_id)

        self.add_node("SHIP-NORTH", "Shipment", status="DELIVERED")
        self.add_node("SHIP-SOUTH", "Shipment", status="DELIVERED")
        self.add_node("STORE-NORTH", "Location", name="North Market", kind="STORE")
        self.add_node("STORE-SOUTH", "Location", name="South Market", kind="STORE")
        for lot_id in ("LOT-GRANOLA-101", "LOT-GRANOLA-102"):
            self.add_edge(lot_id, "IN_SHIPMENT", "SHIP-NORTH")
        self.add_edge("LOT-BITES-201", "IN_SHIPMENT", "SHIP-SOUTH")
        self.add_edge("SHIP-NORTH", "DELIVERED_TO", "STORE-NORTH")
        self.add_edge("SHIP-SOUTH", "DELIVERED_TO", "STORE-SOUTH")

        self.add_node("OP-001", "Operator", name="Maya Chen", role="Recall Coordinator")

    def create_alert(self, alert: AlertInput) -> None:
        if alert.ingredient_lot_id not in self.nodes:
            raise ValueError(f"Unknown ingredient lot: {alert.ingredient_lot_id}")
        if alert.alert_id not in self.nodes:
            self.add_node(
                alert.alert_id,
                "Alert",
                hazard=alert.hazard,
                severity=alert.severity,
                description=alert.description,
            )
            self.add_edge(alert.alert_id, "FLAGS", alert.ingredient_lot_id)

    def case_for_alert(self, alert_id: str) -> str | None:
        matches = self._sources(alert_id, "TRIGGERED_BY")
        return matches[0] if matches else None

    def direct_exposures(self, alert_id: str) -> list[Exposure]:
        exposures: list[Exposure] = []
        for ingredient_id in self._targets(alert_id, "FLAGS"):
            for run_id in self._targets(ingredient_id, "USED_IN"):
                for lot_id in self._targets(run_id, "CREATED"):
                    evidence_id = f"EVD-DIRECT-{lot_id}"
                    evidence = EvidencePath(
                        evidence_id=evidence_id,
                        exposure_type="DIRECT",
                        nodes=[alert_id, ingredient_id, run_id, lot_id],
                        relationships=["FLAGS", "USED_IN", "CREATED"],
                        reason="The flagged ingredient lot was used directly in the production run that created this lot.",
                        query_id="Q-DIRECT-LINEAGE",
                    )
                    exposures.append(Exposure(lot_id, self.nodes[lot_id].properties["sku"], "DIRECT", evidence))
        return exposures

    def _has_validated_cleaning(self, line_id: str, after: datetime, before: datetime) -> bool:
        for cleaning_id in self._targets(line_id, "HAD_CLEANING"):
            cleaning = self.nodes[cleaning_id].properties
            occurred_at = _dt(cleaning["occurred_at"])
            if cleaning.get("validated") is True and after < occurred_at <= before:
                return True
        return False

    def cross_contact_exposures(self, alert_id: str, window_minutes: int) -> list[Exposure]:
        exposures: list[Exposure] = []
        for ingredient_id in self._targets(alert_id, "FLAGS"):
            for source_run_id in self._targets(ingredient_id, "USED_IN"):
                source = self.nodes[source_run_id].properties
                source_end = _dt(source["ended_at"])
                limit = source_end + timedelta(minutes=window_minutes)
                for line_id in self._targets(source_run_id, "RAN_ON"):
                    for adjacent_run_id in self._sources(line_id, "RAN_ON"):
                        if adjacent_run_id == source_run_id:
                            continue
                        adjacent_start = _dt(self.nodes[adjacent_run_id].properties["started_at"])
                        if not (source_end < adjacent_start <= limit):
                            continue
                        if self._has_validated_cleaning(line_id, source_end, adjacent_start):
                            continue
                        for lot_id in self._targets(adjacent_run_id, "CREATED"):
                            evidence = EvidencePath(
                                evidence_id=f"EVD-CROSS-{lot_id}",
                                exposure_type="CROSS_CONTACT",
                                nodes=[alert_id, ingredient_id, source_run_id, line_id, adjacent_run_id, lot_id],
                                relationships=["FLAGS", "USED_IN", "RAN_ON", "RAN_ON_REVERSE", "CREATED"],
                                reason=f"This lot was produced on {line_id} within {window_minutes} minutes and no validated cleaning occurred between runs.",
                                query_id="Q-SHARED-LINE-EXPOSURE",
                            )
                            exposures.append(Exposure(lot_id, self.nodes[lot_id].properties["sku"], "CROSS_CONTACT", evidence))
        return exposures

    def locations_for_lots(self, lot_ids: Iterable[str]) -> list[str]:
        locations: set[str] = set()
        for lot_id in lot_ids:
            for shipment_id in self._targets(lot_id, "IN_SHIPMENT"):
                locations.update(self._targets(shipment_id, "DELIVERED_TO"))
        return sorted(locations)

    def product_lot_count(self) -> int:
        return sum(node.label == "ProductLot" for node in self.nodes.values())

    def create_case(self, alert: AlertInput, exposures: list[Exposure]) -> str:
        case_id = f"CASE-{alert.alert_id.removeprefix('ALERT-')}"
        self.add_node(
            case_id,
            "RecallCase",
            status="AWAITING_APPROVAL",
            decision="RECALL" if exposures else "CLEAR",
            policy_version="lotline-policy-v1",
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self.add_edge(case_id, "TRIGGERED_BY", alert.alert_id)

        seen: set[str] = set()
        for exposure in exposures:
            if exposure.lot_id in seen:
                continue
            seen.add(exposure.lot_id)
            evidence = exposure.evidence
            self.add_node(evidence.evidence_id, "Evidence", **evidence.to_dict())
            self.add_edge(case_id, "AFFECTS", exposure.lot_id)
            self.add_edge(case_id, "HAS_EVIDENCE", evidence.evidence_id)
            action_id = f"ACT-QUARANTINE-{exposure.lot_id}"
            key = sha256(f"{case_id}|QUARANTINE|{exposure.lot_id}".encode()).hexdigest()
            self.add_node(action_id, "Action", action_type="QUARANTINE", status="PROPOSED", idempotency_key=key)
            self.add_edge(case_id, "HAS_ACTION", action_id)
            self.add_edge(action_id, "TARGETS", exposure.lot_id)
            self.add_edge(action_id, "SUPPORTED_BY", evidence.evidence_id)

        for location_id in self.locations_for_lots(seen):
            action_id = f"ACT-NOTIFY-{location_id}"
            key = sha256(f"{case_id}|CREATE_NOTIFICATION_TASK|{location_id}".encode()).hexdigest()
            self.add_node(action_id, "Action", action_type="CREATE_NOTIFICATION_TASK", status="PROPOSED", idempotency_key=key)
            self.add_edge(case_id, "HAS_ACTION", action_id)
            self.add_edge(action_id, "TARGETS", location_id)
        return case_id

    def approve_case(self, case_id: str, operator_id: str) -> dict[str, Any]:
        case = self._require_case(case_id)
        if operator_id not in self.nodes or self.nodes[operator_id].label != "Operator":
            raise PermissionError("Unknown recall operator")
        if case.properties["status"] == "COMPLETED":
            return self.case_snapshot(case_id)
        case.properties["status"] = "APPROVED"
        for action_id in self._targets(case_id, "HAS_ACTION"):
            action = self.nodes[action_id]
            if action.properties["status"] == "PROPOSED":
                action.properties["status"] = "APPROVED"
            self.add_edge(operator_id, "APPROVED", action_id)
        return self.case_snapshot(case_id)

    def execute_case(self, case_id: str) -> ActionResult:
        case = self._require_case(case_id)
        if case.properties["status"] not in {"APPROVED", "COMPLETED"}:
            raise PermissionError("Recall actions require operator approval")
        new_effects = 0
        existing_effects = 0
        effects: list[dict[str, Any]] = []
        for action_id in self._targets(case_id, "HAS_ACTION"):
            action = self.nodes[action_id]
            key = action.properties["idempotency_key"]
            if key in self.completed_effects:
                existing_effects += 1
                effects.append(self.completed_effects[key])
                continue
            target_id = self._targets(action_id, "TARGETS")[0]
            action_type = action.properties["action_type"]
            if action_type == "QUARANTINE":
                self.nodes[target_id].properties["status"] = "QUARANTINED"
                outcome = "LOT_QUARANTINED"
            else:
                outcome = "NOTIFICATION_TASK_CREATED"
            action.properties["status"] = "COMPLETED"
            effect = {
                "action_id": action_id,
                "action_type": action_type,
                "target_id": target_id,
                "outcome": outcome,
                "idempotency_key": key,
            }
            self.completed_effects[key] = effect
            effects.append(effect)
            new_effects += 1
        case.properties["status"] = "COMPLETED"
        return ActionResult(case_id, "COMPLETED", new_effects, existing_effects, effects)

    def _require_case(self, case_id: str) -> Node:
        node = self.nodes.get(case_id)
        if node is None or node.label != "RecallCase":
            raise KeyError(f"Unknown recall case: {case_id}")
        return node

    def case_snapshot(self, case_id: str) -> dict[str, Any]:
        case = self._require_case(case_id)
        affected_ids = sorted(self._targets(case_id, "AFFECTS"))
        evidence = []
        for evidence_id in self._targets(case_id, "HAS_EVIDENCE"):
            evidence.append(dict(self.nodes[evidence_id].properties))
        actions = []
        for action_id in self._targets(case_id, "HAS_ACTION"):
            action = self.nodes[action_id]
            targets = self._targets(action_id, "TARGETS")
            actions.append({**action.properties, "target_id": targets[0] if targets else None})
        return {
            "case_id": case_id,
            "runtime": self.runtime_status,
            "status": case.properties["status"],
            "decision": case.properties["decision"],
            "policy_version": case.properties["policy_version"],
            "affected_lots": affected_ids,
            "affected_lot_count": len(affected_ids),
            "safe_lots_spared": self.product_lot_count() - len(affected_ids),
            "locations": self.locations_for_lots(affected_ids),
            "evidence": sorted(evidence, key=lambda item: item["id"]),
            "actions": sorted(actions, key=lambda item: item["id"]),
        }
