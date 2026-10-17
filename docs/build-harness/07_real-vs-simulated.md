# Real vs Simulated

| Capability | Status | Evidence | Notes |
|---|---|---|---|
| Agent orchestration | REAL — LOCAL | Test and API runs | Executes real Python code |
| HTTP API | REAL — LOCAL | `api-smoke.json` | Bound to localhost during smoke test |
| Approval gate | REAL — CLOUD + LOCAL | Cloud proof + unit test | Operator approval persisted in graph |
| Idempotent effects | REAL — CLOUD + LOCAL | Cloud replay + unit test | Receipts persist; downstream effects remain synthetic |
| Supply-chain data | MOCKED | Seed code | Northstar Foods is fictional |
| Quarantine effects | SIMULATED | `demo-run.json` | Changes synthetic lot status only |
| Notification tasks | SIMULATED | `demo-run.json` | No email/SMS is sent |
| Graph runtime | REAL — CLOUD / MOCKED fallback | Cloud evidence + runtime health labels | Runtime always disclosed |
| FalkorDB integration | VERIFIED | `evidence/cloud-demo-run.json` | Retained graph named in evidence |
| Public site | REAL — CLOUD evidence playback | Public deployment + cloud receipt | Loads sanitized receipt at runtime; no mutation credential |

README, API health, evidence, and UI labels distinguish `REAL — CLOUD` from `MOCKED`. The public build is explicitly evidence playback, not a live operational database session. Making the public mutation API live is intentionally blocked until authentication, rate limiting, and concurrency controls exist.
