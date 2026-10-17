# LotLine

LotLine is a graph-native food-recall agent. Given a safety alert about an ingredient lot, it traces direct use and shared-line cross-contact, proposes the smallest policy-supported recall set, waits for operator approval, executes quarantine and notification-task effects, and records explainable evidence paths.

## Verified status

LotLine has two explicit runtimes:

- **REAL — CLOUD:** the FalkorDB adapter, fixed Cypher traversals, approval gate, execution effects, evidence paths, and idempotent replay were verified against FalkorDB Cloud on October 17, 2026. The retained proof graph is `lotline_proof_20261017_002910`; its machine-readable result is in `evidence/cloud-demo-run.json`.
- **MOCKED — LOCAL:** the deterministic in-memory adapter keeps development and judging reproducible when cloud credentials are unavailable. It exercises the same case semantics but must not be presented as FalkorDB infrastructure.

The cloud credential is never committed. Supply it through environment variables or an ignored `.env` file.

## Run the proof

From this directory:

```powershell
python -m unittest discover -s tests -v
python demo.py
```

Expected core result:

- affected lots: `LOT-GRANOLA-101`, `LOT-GRANOLA-102`, `LOT-BITES-201`;
- `LOT-GRANOLA-103` is excluded because a validated cleaning occurred before its run;
- seven safe product lots are spared;
- five first-run effects: three quarantines and two notification tasks;
- replay produces zero new effects;
- evidence is written to `evidence/demo-run.json`.

## Run the presentation frontend

The six-section frontend uses the two supplied reference artworks unchanged as project assets. It combines them through responsive CSS composition and replaces all copy with LotLine's verified project narrative.

For an offline evidence playback:

```powershell
python -m lotline.api
```

Open `http://127.0.0.1:8765`. The interface labels this mode as verified evidence playback.

For a live FalkorDB-backed replay, configure the cloud environment described in `CLOUD.md`, then run:

```powershell
python -m lotline.api_cloud
```

Open the same URL. The interface detects `REAL — CLOUD`, seeds a fresh graph, analyzes the alert, records operator approval, executes five effects, and immediately replays execution to prove that zero duplicates are created.

## API endpoints

```powershell
python -m lotline.api
```

Endpoints:

- `GET /health`
- `POST /v1/alerts/analyze`
- `GET /v1/cases/{case_id}`
- `POST /v1/cases/{case_id}/approve`
- `POST /v1/cases/{case_id}/execute`

The local health response deliberately says `MOCKED` so the fallback cannot be mistaken for real FalkorDB execution. The cloud health response exposes the real graph name and runtime.

## Graph model

```text
(Supplier)-[:PRODUCED]->(IngredientLot)
(IngredientLot)-[:USED_IN]->(ProductionRun)
(ProductionRun)-[:RAN_ON]->(Line)
(Line)-[:HAD_CLEANING]->(CleaningEvent)
(ProductionRun)-[:CREATED]->(ProductLot)
(ProductLot)-[:IN_SHIPMENT]->(Shipment)
(Shipment)-[:DELIVERED_TO]->(Location)
(Alert)-[:FLAGS]->(IngredientLot)
(RecallCase)-[:AFFECTS]->(ProductLot)
(RecallCase)-[:HAS_ACTION]->(Action)
(Action)-[:SUPPORTED_BY]->(Evidence)
(Operator)-[:APPROVED]->(Action)
```

Fixed FalkorDB queries live in `lotline/cypher.py`.

## Cloud proof summary

- affected lots: `LOT-GRANOLA-101`, `LOT-GRANOLA-102`, and cross-contact lot `LOT-BITES-201`;
- seven safe lots spared;
- five first-run effects: three quarantines and two notification tasks;
- replay: zero new effects and five existing effects;
- final case status: `COMPLETED`;
- regression suite: six tests passing.

## AI assistance disclosure

The architecture, implementation, documentation, and tests were produced with OpenAI Codex assistance under user direction. The participant remains responsible for reviewing, understanding, verifying, and accurately presenting the code and technical decisions.

## Non-claims

This prototype does not validate supplier statements, predict contamination, provide regulatory compliance, replace food-safety professionals, or establish production readiness. All company and supply-chain data are synthetic.
