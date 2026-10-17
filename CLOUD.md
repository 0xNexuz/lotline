# Run LotLine on FalkorDB Cloud without Docker

The official FalkorDB Python client is installed in `.venv`.

Set the cloud connection URL in the current PowerShell session. Do not save it
in the repository or paste it into project documentation:

```powershell
$env:FALKORDB_URL = '<copy the complete provider URI here>'
.\.venv\Scripts\python.exe cloud_demo.py
```

The script creates a fresh timestamped graph, seeds only synthetic Northstar
Foods data, verifies the affected set, approval gate, five first-run effects,
and zero replay effects, then writes `evidence/cloud-demo-run.json`.

It deliberately retains the proof graph for inspection. It does not delete or
modify any pre-existing graph.

To run the HTTP backend against the same cloud database:

```powershell
$env:FALKORDB_GRAPH = 'a_fresh_empty_graph_name'
.\.venv\Scripts\python.exe -m lotline.api_cloud
```

Then seed it once with `POST /v1/seed` before analyzing an alert. The API refuses
to seed a non-empty graph.

Discrete variables are also supported:

```text
FALKORDB_HOST
FALKORDB_PORT
FALKORDB_USERNAME
FALKORDB_PASSWORD
FALKORDB_TLS=true
```

Prefer `FALKORDB_URL` because it preserves the provider's exact scheme and port
in one value. Copy the URI FalkorDB Cloud supplies without changing its scheme:
the Free resource can use `falkor://` without TLS, while TLS-enabled resources
use `falkors://`. For discrete variables, set `FALKORDB_TLS=false` when the
provider gives a non-TLS URI. The public Vercel site needs no cloud credential;
it plays back the retained, sanitized proof artifact.
