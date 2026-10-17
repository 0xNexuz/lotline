"""Fixed Cypher used by the real FalkorDB adapter.

The local Windows run uses MemoryGraphStore because no FalkorDB runtime is
available. These queries are the load-bearing contract to verify against a real
FalkorDB instance through Docker or Cloud.
"""

DIRECT_EXPOSURE = """
MATCH p=(a:Alert {id: $alert_id})-[:FLAGS]->(i:IngredientLot)
        -[:USED_IN]->(r:ProductionRun)-[:CREATED]->(lot:ProductLot)
RETURN lot.id AS lot_id, lot.sku AS sku,
       [n IN nodes(p) | n.id] AS nodes,
       [rel IN relationships(p) | type(rel)] AS relationships
ORDER BY lot.id
""".strip()

CROSS_CONTACT_EXPOSURE = """
MATCH (a:Alert {id: $alert_id})-[:FLAGS]->(:IngredientLot)
      -[:USED_IN]->(source:ProductionRun)-[:RAN_ON]->(line:Line)
      <-[:RAN_ON]-(adjacent:ProductionRun)-[:CREATED]->(lot:ProductLot)
WHERE adjacent.id <> source.id
  AND adjacent.started_at > source.ended_at
  AND adjacent.started_at <= source.ended_at + $window_seconds
  AND NOT EXISTS {
    MATCH (line)-[:HAD_CLEANING]->(cleaning:CleaningEvent)
    WHERE cleaning.validated = true
      AND cleaning.occurred_at > source.ended_at
      AND cleaning.occurred_at <= adjacent.started_at
  }
RETURN DISTINCT lot.id AS lot_id, lot.sku AS sku,
       source.id AS source_run, line.id AS line_id,
       adjacent.id AS adjacent_run
ORDER BY lot.id
""".strip()

IDEMPOTENT_QUARANTINE = """
MATCH (c:RecallCase {id: $case_id}), (lot:ProductLot {id: $lot_id})
MERGE (action:Action {idempotency_key: $idempotency_key})
ON CREATE SET action.id = $action_id,
              action.action_type = 'QUARANTINE',
              action.status = 'COMPLETED',
              action.created_at = timestamp()
MERGE (c)-[:HAS_ACTION]->(action)
MERGE (action)-[:TARGETS]->(lot)
SET lot.status = 'QUARANTINED'
RETURN action.id AS action_id, lot.id AS lot_id, lot.status AS status
""".strip()
