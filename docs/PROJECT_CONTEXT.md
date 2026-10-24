# LotLine Project Context

Last updated: 2026-10-24. Keep this record evidence-based and free of secrets.

## Identity and current state

- Project: LotLine, a graph-native food-recall decision demonstrator.
- Repository: https://github.com/0xNexuz/lotline (public).
- Branch and last audited implementation commit: `main`, `723028a`. Check Git for the current HEAD before acting.
- Current stage: READINESS / SUBMISSION_PREPARATION.
- Status: implementation and source verification complete; Vercel still serves the previous interface as of 2026-10-24, so the latest UI release is not yet verified live.
- Approved scope: product audit, UI/navigation refinement, documentation, public GitHub and Vercel release, and submission-answer preparation. No final hackathon submission was authorized or performed.

## Hackathon

- Event: Graph Hacks: Context for AI Agents, WeMakeDevs × FalkorDB.
- Track: Agents That Act on Connected Data.
- Official event and rules: https://www.wemakedevs.org/hackathons/falkordb and https://www.wemakedevs.org/hackathons/falkordb/rules.
- Published deadline: 2026-10-18 23:59 IST. On 2026-10-24 this date has passed; form availability and registration are unverified.
- Required submission package: public repository, README with setup and graph model, essential Cypher, demo video, live deployment or complete local setup, and track selection. AI assistance is disclosed in README as required by the rules.

## Architecture and proof boundary

- Stack: Python deterministic policy agent, fixed Cypher queries, FalkorDB Cloud, static HTML/CSS/JavaScript replay on Vercel.
- Graph decision: ingredient lineage plus shared-line adjacency inside a 60-minute window; validated cleaning stops propagation. Human approval gates idempotent graph effects.
- Real integration: retained FalkorDB Cloud graph `lotline_proof_20261017_002910` and sanitized `evidence/cloud-demo-run.json`. It records three affected lots, seven safe lots spared, five first-run effects, and zero new effects on replay.
- Mocked/simulated: synthetic supply-chain source data; six adversarial scenarios use the MemoryGraphStore adapter; quarantine is a graph status, and notification is a task record, not an outbound message.
- Public security boundary: Vercel serves static, credential-free playback only. The cloud-mutating Python API stays localhost-only without production authentication, rate limiting, concurrency/partial-failure hardening, and observability.

## Verified milestones and open gates

| Date | Evidence | Result |
|---|---|---|
| 2026-10-17 | Retained cloud run, `evidence/cloud-demo-run.json` | VERIFIED real cloud workflow |
| 2026-10-17 | Six-scenario benchmark, `evidence/scenario-benchmark.json` | VERIFIED mocked regression matrix |
| 2026-10-24 | `npm run check`, `npm run build` | PASS; ten build assets |
| 2026-10-24 | `python -m unittest discover -s tests -v` via bundled Python | PASS; seven tests |
| 2026-10-24 | GitHub Actions run 39060990863 for `723028a` | PASS |
| 2026-10-24 | Public Vercel browser inspection | OLD interface still live; latest release UNVERIFIED |

Open submission gates: latest Vercel release verification, public/unlisted YouTube demo video, registration/form availability confirmation, and participant review of answers. No real company integrations or operational deployment claim is approved.

## Decision log

### 2026-10-17 — Keep public proof credential-free

- Decision: publish a static replay of a sanitized real-cloud receipt; keep cloud mutations in a local-only API.
- Reason: the API lacks production access control and failure hardening; no credential should reach the browser.
- Status: APPROVED and IMPLEMENTED.

### 2026-10-17 — Expose evidence and scenario boundary honestly

- Decision: use the actual cloud receipt for the public replay, retain six mocked adversarial regressions, and label graph-only effects as simulated.
- Reason: judges should see both a real FalkorDB mechanism and the exact limits of the proof.
- Status: IMPLEMENTED and VERIFIED in source; latest public deployment pending verification.

## Next action

Verify the linked Vercel target, release the tested source, and check the short public URL and cloud receipt. Then provide the copy-ready form answers while flagging the missing video and elapsed published deadline. Do not submit the form on the participant's behalf.
