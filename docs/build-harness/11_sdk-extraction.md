# SDK Extraction

## Candidate primitive

`GraphActionReceipt`: a reusable pattern joining policy version, evidence path, approval, idempotency key, target, and outcome.

Reuse value: high for operational agents.
Extraction cost: medium.
Priority: P2, after the hackathon release.

Do not extract yet:

- Food-recall policy.
- HTTP API.
- MemoryGraphStore.

Extraction is premature until concurrent and partial-failure transaction behavior is verified.
