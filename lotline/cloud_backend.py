from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any

from falkordb import FalkorDB

from .models import ActionResult, AlertInput, EvidencePath, Exposure


SEED_QUERY = """
CREATE
  (sup:Supplier {id:'SUP-01', name:'Almond Cooperative'}),
  (i42:IngredientLot {id:'ING-ALM-042', ingredient:'almond meal'}),
  (i43:IngredientLot {id:'ING-ALM-043', ingredient:'almond meal'}),
  (line1:Line {id:'LINE-01', name:'Line 1'}),
  (line2:Line {id:'LINE-02', name:'Line 2'}),
  (r100:ProductionRun {id:'RUN-100', started_at:1792134800, ended_at:1792138400}),
  (r101:ProductionRun {id:'RUN-101', started_at:1792138700, ended_at:1792139300}),
  (r102:ProductionRun {id:'RUN-102', started_at:1792140200, ended_at:1792142000}),
  (r200:ProductionRun {id:'RUN-200', started_at:1792142600, ended_at:1792147400}),
  (clean:CleaningEvent {id:'CLEAN-01', occurred_at:1792139600, validated:true}),
  (l101:ProductLot {id:'LOT-GRANOLA-101', sku:'GRANOLA-ALMOND', status:'AVAILABLE'}),
  (l102:ProductLot {id:'LOT-GRANOLA-102', sku:'GRANOLA-ALMOND', status:'AVAILABLE'}),
  (l201:ProductLot {id:'LOT-BITES-201', sku:'ENERGY-BITES', status:'AVAILABLE'}),
  (l103:ProductLot {id:'LOT-GRANOLA-103', sku:'GRANOLA-ALMOND', status:'AVAILABLE'}),
  (l104:ProductLot {id:'LOT-GRANOLA-104', sku:'GRANOLA-ALMOND', status:'AVAILABLE'}),
  (l105:ProductLot {id:'LOT-GRANOLA-105', sku:'GRANOLA-ALMOND', status:'AVAILABLE'}),
  (l106:ProductLot {id:'LOT-GRANOLA-106', sku:'GRANOLA-ALMOND', status:'AVAILABLE'}),
  (l107:ProductLot {id:'LOT-GRANOLA-107', sku:'GRANOLA-ALMOND', status:'AVAILABLE'}),
  (l108:ProductLot {id:'LOT-GRANOLA-108', sku:'GRANOLA-ALMOND', status:'AVAILABLE'}),
  (l109:ProductLot {id:'LOT-GRANOLA-109', sku:'GRANOLA-ALMOND', status:'AVAILABLE'}),
  (sn:Shipment {id:'SHIP-NORTH', status:'DELIVERED'}),
  (ss:Shipment {id:'SHIP-SOUTH', status:'DELIVERED'}),
  (north:Location {id:'STORE-NORTH', name:'North Market', kind:'STORE'}),
  (south:Location {id:'STORE-SOUTH', name:'South Market', kind:'STORE'}),
  (op:Operator {id:'OP-001', name:'Maya Chen', role:'Recall Coordinator'}),
  (sup)-[:PRODUCED]->(i42), (sup)-[:PRODUCED]->(i43),
  (i42)-[:USED_IN]->(r100), (i43)-[:USED_IN]->(r200),
  (r100)-[:RAN_ON]->(line1), (r101)-[:RAN_ON]->(line1),
  (r102)-[:RAN_ON]->(line1), (r200)-[:RAN_ON]->(line2),
  (line1)-[:HAD_CLEANING]->(clean),
  (r100)-[:CREATED]->(l101), (r100)-[:CREATED]->(l102),
  (r101)-[:CREATED]->(l201), (r102)-[:CREATED]->(l103),
  (r200)-[:CREATED]->(l104), (r200)-[:CREATED]->(l105),
  (r200)-[:CREATED]->(l106), (r200)-[:CREATED]->(l107),
  (r200)-[:CREATED]->(l108), (r200)-[:CREATED]->(l109),
  (l101)-[:IN_SHIPMENT]->(sn), (l102)-[:IN_SHIPMENT]->(sn),
  (l201)-[:IN_SHIPMENT]->(ss),
  (sn)-[:DELIVERED_TO]->(north), (ss)-[:DELIVERED_TO]->(south)
RETURN count(*) AS seeded
""".strip()


DIRECT_QUERY = """
MATCH p=(a:Alert {id:$alert_id})-[:FLAGS]->(i:IngredientLot)
        -[:USED_IN]->(r:ProductionRun)-[:CREATED]->(lot:ProductLot)
RETURN lot.id, lot.sku,
       [n IN nodes(p) | n.id],
       [rel IN relationships(p) | type(rel)]
ORDER BY lot.id
""".strip()


CROSS_CONTACT_QUERY = """
MATCH (a:Alert {id:$alert_id})-[:FLAGS]->(ingredient:IngredientLot)
      -[:USED_IN]->(source:ProductionRun)-[:RAN_ON]->(line:Line)
      <-[:RAN_ON]-(adjacent:ProductionRun)-[:CREATED]->(lot:ProductLot)
WHERE adjacent.id <> source.id
  AND adjacent.started_at > source.ended_at
  AND adjacent.started_at <= source.ended_at + $window_seconds
OPTIONAL MATCH (line)-[:HAD_CLEANING]->(cleaning:CleaningEvent)
WHERE cleaning.validated = true
  AND cleaning.occurred_at > source.ended_at
  AND cleaning.occurred_at <= adjacent.started_at
WITH ingredient, source, line, adjacent, lot, collect(cleaning) AS cleanings
WHERE size(cleanings) = 0
RETURN DISTINCT lot.id, lot.sku, ingredient.id, source.id, line.id, adjacent.id
ORDER BY lot.id
""".strip()


def cloud_configured() -> bool:
    return bool(os.environ.get("FALKORDB_URL") or os.environ.get("FALKORDB_HOST"))


def _truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


class FalkorDBCloudAgent:
    """LotLine agent whose state and traversals execute in FalkorDB Cloud."""

    runtime_status = "REAL — CLOUD"

    def __init__(self, graph_name: str | None = None) -> None:
        connection_url = os.environ.get("FALKORDB_URL")
        timeout = int(os.environ.get("FALKORDB_TIMEOUT_SECONDS", "15"))
        if connection_url:
            self.db = FalkorDB.from_url(
                connection_url,
                socket_connect_timeout=timeout,
                socket_timeout=timeout,
                health_check_interval=30,
            )
        else:
            host = os.environ.get("FALKORDB_HOST")
            if not host:
                raise RuntimeError("Set FALKORDB_URL or FALKORDB_HOST for cloud mode")
            password = os.environ.get("FALKORDB_PASSWORD")
            if not password:
                raise RuntimeError("FALKORDB_PASSWORD is required for cloud mode")
            self.db = FalkorDB(
                host=host,
                port=int(os.environ.get("FALKORDB_PORT", "6379")),
                username=os.environ.get("FALKORDB_USERNAME", "default"),
                password=password,
                ssl=_truthy(os.environ.get("FALKORDB_TLS", "true")),
                ssl_check_hostname=True,
                ssl_cert_reqs="required",
                socket_connect_timeout=timeout,
                socket_timeout=timeout,
                health_check_interval=30,
            )
        self.graph_name = graph_name or os.environ.get("FALKORDB_GRAPH") or self._new_graph_name()
        self.graph = self.db.select_graph(self.graph_name)
        self.cross_contact_window_minutes = 60

    @staticmethod
    def _new_graph_name() -> str:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        return f"lotline_proof_{stamp}"

    def ping(self) -> dict[str, Any]:
        result = self.graph.query("RETURN 1 AS ok").result_set
        return {"ok": result == [[1]], "graph": self.graph_name, "runtime": self.runtime_status}

    def seed_northstar(self) -> None:
        existing = self.graph.ro_query("MATCH (n) RETURN count(n)").result_set[0][0]
        if existing:
            raise RuntimeError(
                f"Refusing to seed non-empty graph {self.graph_name!r}; choose a fresh FALKORDB_GRAPH"
            )
        self.graph.query(SEED_QUERY)

    def analyze(self, alert: AlertInput) -> dict[str, Any]:
        existing = self.graph.ro_query(
            "MATCH (c:RecallCase)-[:TRIGGERED_BY]->(:Alert {id:$alert_id}) RETURN c.id",
            {"alert_id": alert.alert_id},
        ).result_set
        if existing:
            return self.inspect(existing[0][0])
        created = self.graph.query(
            """
            MATCH (ingredient:IngredientLot {id:$ingredient_lot_id})
            CREATE (a:Alert {
              id:$alert_id, hazard:$hazard, severity:$severity, description:$description
            })-[:FLAGS]->(ingredient)
            RETURN a.id
            """,
            {
                "ingredient_lot_id": alert.ingredient_lot_id,
                "alert_id": alert.alert_id,
                "hazard": alert.hazard,
                "severity": alert.severity,
                "description": alert.description,
            },
        ).result_set
        if not created:
            raise ValueError(f"Unknown ingredient lot: {alert.ingredient_lot_id}")
        direct = self._direct_exposures(alert.alert_id)
        cross = self._cross_contact_exposures(alert.alert_id)
        exposures = direct + cross if alert.severity == "high" else direct
        return self._create_case(alert, exposures)

    def _direct_exposures(self, alert_id: str) -> list[Exposure]:
        rows = self.graph.ro_query(DIRECT_QUERY, {"alert_id": alert_id}).result_set
        return [
            Exposure(
                lot_id,
                sku,
                "DIRECT",
                EvidencePath(
                    f"EVD-DIRECT-{lot_id}", "DIRECT", nodes, relationships,
                    "The flagged ingredient lot was used directly in the run that created this lot.",
                    "Q-DIRECT-LINEAGE",
                ),
            )
            for lot_id, sku, nodes, relationships in rows
        ]

    def _cross_contact_exposures(self, alert_id: str) -> list[Exposure]:
        rows = self.graph.ro_query(
            CROSS_CONTACT_QUERY,
            {"alert_id": alert_id, "window_seconds": self.cross_contact_window_minutes * 60},
        ).result_set
        return [
            Exposure(
                lot_id,
                sku,
                "CROSS_CONTACT",
                EvidencePath(
                    f"EVD-CROSS-{lot_id}", "CROSS_CONTACT",
                    [alert_id, ingredient_id, source_id, line_id, adjacent_id, lot_id],
                    ["FLAGS", "USED_IN", "RAN_ON", "RAN_ON_REVERSE", "CREATED"],
                    f"Produced on {line_id} within 60 minutes without validated cleaning between runs.",
                    "Q-SHARED-LINE-EXPOSURE",
                ),
            )
            for lot_id, sku, ingredient_id, source_id, line_id, adjacent_id in rows
        ]

    def _create_case(self, alert: AlertInput, exposures: list[Exposure]) -> dict[str, Any]:
        case_id = f"CASE-{alert.alert_id.removeprefix('ALERT-')}"
        self.graph.query(
            """
            MATCH (a:Alert {id:$alert_id})
            CREATE (c:RecallCase {
              id:$case_id, status:'AWAITING_APPROVAL', decision:$decision,
              policy_version:'lotline-policy-v1', created_at:timestamp()
            })-[:TRIGGERED_BY]->(a)
            RETURN c.id
            """,
            {"alert_id": alert.alert_id, "case_id": case_id, "decision": "RECALL" if exposures else "CLEAR"},
        )
        seen: set[str] = set()
        for exposure in exposures:
            if exposure.lot_id in seen:
                continue
            seen.add(exposure.lot_id)
            evidence = exposure.evidence
            action_id = f"ACT-QUARANTINE-{exposure.lot_id}"
            key = sha256(f"{case_id}|QUARANTINE|{exposure.lot_id}".encode()).hexdigest()
            self.graph.query(
                """
                MATCH (c:RecallCase {id:$case_id}), (lot:ProductLot {id:$lot_id})
                CREATE (e:Evidence {
                  id:$evidence_id, exposure_type:$exposure_type, nodes_json:$nodes_json,
                  relationships_json:$relationships_json, reason:$reason, query_id:$query_id
                })
                CREATE (action:Action {
                  id:$action_id, action_type:'QUARANTINE', status:'PROPOSED', idempotency_key:$key
                })
                CREATE (c)-[:AFFECTS]->(lot), (c)-[:HAS_EVIDENCE]->(e),
                       (c)-[:HAS_ACTION]->(action), (action)-[:TARGETS]->(lot),
                       (action)-[:SUPPORTED_BY]->(e)
                RETURN action.id
                """,
                {
                    "case_id": case_id, "lot_id": exposure.lot_id,
                    "evidence_id": evidence.evidence_id, "exposure_type": evidence.exposure_type,
                    "nodes_json": json.dumps(evidence.nodes),
                    "relationships_json": json.dumps(evidence.relationships),
                    "reason": evidence.reason, "query_id": evidence.query_id,
                    "action_id": action_id, "key": key,
                },
            )
        locations = [
            row[0]
            for row in self.graph.ro_query(
                """
                MATCH (:RecallCase {id:$case_id})-[:AFFECTS]->(:ProductLot)
                      -[:IN_SHIPMENT]->(:Shipment)-[:DELIVERED_TO]->(loc:Location)
                RETURN DISTINCT loc.id ORDER BY loc.id
                """,
                {"case_id": case_id},
            ).result_set
        ]
        for location_id in locations:
            action_id = f"ACT-NOTIFY-{location_id}"
            key = sha256(f"{case_id}|CREATE_NOTIFICATION_TASK|{location_id}".encode()).hexdigest()
            self.graph.query(
                """
                MATCH (c:RecallCase {id:$case_id}), (loc:Location {id:$location_id})
                CREATE (action:Action {
                  id:$action_id, action_type:'CREATE_NOTIFICATION_TASK',
                  status:'PROPOSED', idempotency_key:$key
                })
                CREATE (c)-[:HAS_ACTION]->(action), (action)-[:TARGETS]->(loc)
                RETURN action.id
                """,
                {"case_id": case_id, "location_id": location_id, "action_id": action_id, "key": key},
            )
        return self.inspect(case_id)

    def approve(self, case_id: str, operator_id: str) -> dict[str, Any]:
        rows = self.graph.query(
            """
            MATCH (c:RecallCase {id:$case_id}), (op:Operator {id:$operator_id})
            SET c.status = CASE WHEN c.status = 'COMPLETED' THEN 'COMPLETED' ELSE 'APPROVED' END
            WITH c, op
            MATCH (c)-[:HAS_ACTION]->(action:Action)
            SET action.status = CASE WHEN action.status = 'COMPLETED' THEN 'COMPLETED' ELSE 'APPROVED' END
            MERGE (op)-[:APPROVED]->(action)
            RETURN c.status
            """,
            {"case_id": case_id, "operator_id": operator_id},
        ).result_set
        if not rows:
            raise PermissionError("Unknown case or recall operator")
        return self.inspect(case_id)

    def execute(self, case_id: str) -> dict[str, Any]:
        states = self.graph.ro_query(
            "MATCH (c:RecallCase {id:$case_id}) RETURN c.status", {"case_id": case_id}
        ).result_set
        if not states or states[0][0] not in {"APPROVED", "COMPLETED"}:
            raise PermissionError("Recall actions require operator approval")
        actions = self.graph.ro_query(
            """
            MATCH (:RecallCase {id:$case_id})-[:HAS_ACTION]->(a:Action)-[:TARGETS]->(target)
            RETURN a.id, a.action_type, a.idempotency_key, target.id ORDER BY a.id
            """,
            {"case_id": case_id},
        ).result_set
        new_effects = existing_effects = 0
        effects: list[dict[str, Any]] = []
        for action_id, action_type, key, target_id in actions:
            outcome = "LOT_QUARANTINED" if action_type == "QUARANTINE" else "NOTIFICATION_TASK_CREATED"
            rows = self.graph.query(
                """
                MATCH (:RecallCase {id:$case_id})-[:HAS_ACTION]->(a:Action {id:$action_id})
                      -[:TARGETS]->(target {id:$target_id})
                MERGE (effect:Effect {idempotency_key:$key})
                ON CREATE SET effect.id=$effect_id, effect.outcome=$outcome,
                              effect.execution_count=1, effect.created_at=timestamp()
                ON MATCH SET effect.execution_count=effect.execution_count + 1,
                             effect.last_replayed_at=timestamp()
                MERGE (a)-[:PRODUCED]->(effect)
                SET a.status='COMPLETED'
                SET target.status = CASE WHEN $action_type = 'QUARANTINE' THEN 'QUARANTINED' ELSE target.status END
                RETURN effect.execution_count
                """,
                {
                    "case_id": case_id, "action_id": action_id, "target_id": target_id,
                    "key": key, "effect_id": f"EFFECT-{action_id}",
                    "outcome": outcome, "action_type": action_type,
                },
            ).result_set
            is_new = rows[0][0] == 1
            new_effects += int(is_new)
            existing_effects += int(not is_new)
            effects.append({
                "action_id": action_id, "action_type": action_type,
                "target_id": target_id, "outcome": outcome, "idempotency_key": key,
            })
        self.graph.query(
            "MATCH (c:RecallCase {id:$case_id}) SET c.status='COMPLETED' RETURN c.status",
            {"case_id": case_id},
        )
        return ActionResult(case_id, "COMPLETED", new_effects, existing_effects, effects).to_dict()

    def inspect(self, case_id: str) -> dict[str, Any]:
        case_rows = self.graph.ro_query(
            "MATCH (c:RecallCase {id:$case_id}) RETURN c.status, c.decision, c.policy_version",
            {"case_id": case_id},
        ).result_set
        if not case_rows:
            raise KeyError(f"Unknown recall case: {case_id}")
        status, decision, policy_version = case_rows[0]
        affected = [row[0] for row in self.graph.ro_query(
            "MATCH (:RecallCase {id:$case_id})-[:AFFECTS]->(lot:ProductLot) RETURN lot.id ORDER BY lot.id",
            {"case_id": case_id},
        ).result_set]
        total = self.graph.ro_query("MATCH (lot:ProductLot) RETURN count(lot)").result_set[0][0]
        locations = [row[0] for row in self.graph.ro_query(
            """
            MATCH (:RecallCase {id:$case_id})-[:AFFECTS]->(:ProductLot)
                  -[:IN_SHIPMENT]->(:Shipment)-[:DELIVERED_TO]->(loc:Location)
            RETURN DISTINCT loc.id ORDER BY loc.id
            """,
            {"case_id": case_id},
        ).result_set]
        evidence = [{
            "id": row[0], "exposure_type": row[1], "nodes": json.loads(row[2]),
            "relationships": json.loads(row[3]), "reason": row[4], "query_id": row[5],
        } for row in self.graph.ro_query(
            """
            MATCH (:RecallCase {id:$case_id})-[:HAS_EVIDENCE]->(e:Evidence)
            RETURN e.id, e.exposure_type, e.nodes_json, e.relationships_json, e.reason, e.query_id
            ORDER BY e.id
            """,
            {"case_id": case_id},
        ).result_set]
        actions = [{
            "id": row[0], "action_type": row[1], "status": row[2],
            "idempotency_key": row[3], "target_id": row[4],
        } for row in self.graph.ro_query(
            """
            MATCH (:RecallCase {id:$case_id})-[:HAS_ACTION]->(a:Action)-[:TARGETS]->(target)
            RETURN a.id, a.action_type, a.status, a.idempotency_key, target.id ORDER BY a.id
            """,
            {"case_id": case_id},
        ).result_set]
        return {
            "case_id": case_id, "graph_name": self.graph_name, "runtime": self.runtime_status,
            "status": status, "decision": decision, "policy_version": policy_version,
            "affected_lots": affected, "affected_lot_count": len(affected),
            "safe_lots_spared": total - len(affected), "locations": locations,
            "evidence": evidence, "actions": actions,
        }
