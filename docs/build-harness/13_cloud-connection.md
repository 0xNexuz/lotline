# Cloud Connection Addendum

Date: 2026-10-17

## Implemented

- Official `FalkorDB` Python client 1.8.0 installed in `.venv`.
- TLS cloud configuration through `FALKORDB_URL` or discrete environment variables.
- Fresh timestamped proof graph per `cloud_demo.py` run.
- Refusal to seed a non-empty named graph.
- Real Cypher seed, direct-lineage, shared-line/cleaning, case, approval, action, evidence, and replay queries.
- Dedicated cloud HTTP backend in `lotline/api_cloud.py`.
- Cloud adapter compiles and imports successfully.
- Seven local tests, including the six-scenario benchmark, pass after the cloud implementation.

## Current status

FalkorDB Cloud execution: **VERIFIED**

- Runtime: `REAL — CLOUD`
- Retained proof graph: `lotline_proof_20261017_002910`
- Result: 3 affected, 7 spared, 5 first-run effects, 0 replay effects
- Final case state: `COMPLETED`
- Evidence: `evidence/cloud-demo-run.json`

## Reproduce with a new graph

In a local PowerShell session, set the connection URL supplied by FalkorDB Cloud:

```powershell
$env:FALKORDB_URL = '<copy the complete provider URI here>'
```

Then run:

```powershell
.\.venv\Scripts\python.exe cloud_demo.py
```

The script creates a fresh timestamped graph and refuses to seed a non-empty
graph. Copy the provider URI exactly: the Free resource may use `falkor://`,
while TLS-enabled resources use `falkors://`. Never commit the URI or password.
