# Threat Model

## Objective

Prevent incomplete, manipulated, unauthorized, or replayed recall actions from being presented as trustworthy.

## Assets

| Asset | Impact if compromised |
|---|---|
| Lot lineage | Wrong products recalled or missed |
| Cleaning records | False cross-contact inclusion/exclusion |
| Approval authority | Unauthorized inventory changes |
| Evidence paths | Decisions become unauditable |
| Idempotency state | Duplicate tasks or notifications |

## Threats and current defenses

| Threat | Defense | Test | Status |
|---|---|---|---|
| Execute without approval | State gate | Unit test + cloud case transition | VERIFIED |
| Replay action | Deterministic idempotency key | Unit test + zero-new-effect cloud replay | VERIFIED |
| Unsupported quarantine | Evidence relationship required | Unit test + cloud evidence paths | VERIFIED |
| Prompt/model invents query | Fixed queries; model outside decision core | Code inspection | COMPLETE |
| Missing lineage | Unknown lots fail closed | Unit/code path | PARTIAL |
| Compromised source data | No provenance/signature mechanism | None | NOT IMPLEMENTED |
| Concurrent approvals/execution | No transaction test yet | None | NOT IMPLEMENTED |
| Public mutation endpoint abuse | Do not deploy credentialed API; static proof only | Vercel configuration | MITIGATED FOR PUBLIC DEMO |

## Guarantees

- Both runtimes deny execution before approval.
- Replaying the verified FalkorDB case creates zero new effects.
- Every planned quarantine in the cloud proof has a linked evidence path.

## Non-guarantees

- Input records are truthful.
- The prototype satisfies a regulator.
- Concurrent distributed execution is safe.
- The private API is safe to expose without authentication or rate limiting.
