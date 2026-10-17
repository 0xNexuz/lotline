# Invariants

| ID | Invariant | Enforcement | Evidence | Status |
|---|---|---|---|---|
| INV-001 | No recall effect executes before operator approval | Case state check | Approval test + cloud transition | VERIFIED |
| INV-002 | A case-effect key executes at most once | SHA-256 idempotency key + persisted receipt | Replay test + cloud replay | VERIFIED |
| INV-003 | Every quarantine action has one evidence path | `SUPPORTED_BY` relationship | Evidence test + cloud output | VERIFIED |
| INV-004 | A validated cleaning between runs excludes the later run | Time-bounded cleaning traversal | Cleaning test + cloud result | VERIFIED |
| INV-005 | Removing the lot-to-run edge removes direct exposure | Relationship traversal | Load-bearing edge test | VERIFIED — LOCAL ADVERSARIAL TEST |
| INV-006 | Real sponsor claims require real FalkorDB execution | Status labels and README | Health/API output | COMPLETE |

Untested critical invariants:

- Concurrent execution remains idempotent across processes.
- FalkorDB transactions preserve the invariants under partial failure.
- Imported records retain trustworthy provenance.
