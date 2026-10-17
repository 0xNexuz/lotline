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
| Six policy/failure scenarios behave as documented | Scenario matrix | `evidence/scenario-benchmark.json` | VERIFIED — MOCKED |
| Public UI reads the real receipt | Browser flow + build artifact | `/evidence/cloud-demo-run.json` | VERIFIED |

## Verify it yourself

```powershell
python -m unittest discover -s tests -v
python scenario_benchmark.py --write
npm run check
npm run build
```

Expected: seven tests pass, all six benchmark scenarios report `VERIFIED`, and the demo reports three affected lots, seven spared lots, five first-run effects, and zero new replay effects.

No performance number, regulatory claim, sponsor endorsement, or real-company result is claimed.
