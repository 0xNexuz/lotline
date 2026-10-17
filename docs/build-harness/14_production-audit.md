# Production Audit

Date: 2026-10-17

## Verdict

**READY for public hackathon demonstration. NOT READY for operational food-safety use.**

The public artifact is a static, credential-free playback of a retained real
FalkorDB Cloud proof. The credentialed Python API remains localhost-only because
it does not yet have production authentication, authorization, rate limiting,
concurrency hardening, or observability.

## Ranked findings

| Priority | Finding | Resolution / owner |
|---|---|---|
| P0 | Cloud integration had no real execution evidence | RESOLVED — retained cloud graph and sanitized evidence artifact |
| P0 | Public deployment could expose a mutation credential | RESOLVED FOR DEMO — Vercel ships static playback only |
| P1 | Completed-case replay enabled an invalid approval state in the UI | RESOLVED — UI now derives controls from case status |
| P1 | CI used mutable action tags | RESOLVED — action commits pinned; credentials not persisted |
| P1 | Concurrent/partial-failure execution is unverified | OPEN — blocks operational deployment, not static demo |
| P1 | Public API authentication and rate limiting are absent | OPEN — credentialed API must remain private |
| P2 | Only one frozen supply-chain scenario is benchmarked | OPEN — add five adversarial scenarios |
| P2 | Automated accessibility/performance testing is absent | OPEN — add browser CI after submission |

## Evidence ledger

| Claim | Evidence | Status |
|---|---|---|
| FalkorDB executes the workflow | `evidence/cloud-demo-run.json` | VERIFIED |
| Approval gates effects | Unit suite + cloud state transitions | VERIFIED |
| Replay creates no duplicate effects | Cloud replay: 0 new / 5 existing | VERIFIED |
| Exact supplied artwork is used | SHA-256 checks in `scripts/check-site.mjs` | VERIFIED |
| Frontend builds reproducibly | `npm run build` + build manifest | VERIFIED |
| Source contains no pasted cloud password | scoped credential scan | VERIFIED |
| Operational production safety | No auth/concurrency/observability evidence | NOT VERIFIED |

## Ship gates

- [x] Six invariant tests pass.
- [x] Python entry points compile.
- [x] JavaScript syntax and asset-integrity checks pass.
- [x] Production static build succeeds.
- [x] CSP, clickjacking, MIME-sniffing, referrer, and permissions headers configured.
- [x] Keyboard focus, skip link, section navigation, and responsive navigation present.
- [ ] Public repository and production URL recorded in release summary.
- [ ] Remote CI run passes on the public repository.

## Remaining boundary

Passing these gates certifies the demonstrator, not the domain outcome. LotLine
uses synthetic data, does not send email or SMS, does not validate source truth,
and does not replace a qualified food-safety operator.
