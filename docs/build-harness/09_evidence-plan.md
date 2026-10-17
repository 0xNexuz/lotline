# Evidence Plan

| Claim | Required evidence | Current artifact | Status |
|---|---|---|---|
| Three lots affected, seven spared | Deterministic result | `evidence/cloud-demo-run.json` | VERIFIED — CLOUD |
| Cleaning excludes later lot | Passing test | `evidence/test-run.txt` | VERIFIED — MOCKED |
| Approval required | Passing rejection test | `evidence/test-run.txt` | VERIFIED — MOCKED |
| Replay creates zero new effects | First/replay outputs | `evidence/cloud-demo-run.json` | VERIFIED — CLOUD |
| API completes flow | HTTP responses | `evidence/api-smoke.json` | VERIFIED — MOCKED |
| FalkorDB is load-bearing | Real query output + local removal test | Cloud evidence + test suite | VERIFIED |
| Exact reference art retained | SHA-256 comparison | `npm run check` | VERIFIED |
| Public build is reproducible | Build manifest | `dist/build-manifest.json` | VERIFIED LOCALLY |

## Verify it yourself

```powershell
python -m unittest discover -s tests -v
npm run check
npm run build
```

Expected: six tests pass; the demo reports three affected lots, seven spared lots, five first-run effects, and zero new replay effects.

No performance number, regulatory claim, sponsor endorsement, or real-company result is claimed.
