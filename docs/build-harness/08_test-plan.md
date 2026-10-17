# Test Plan

## Objective

Prove the recall set, cleaning exclusion, authorization, evidence, graph dependency, and replay safety.

## Current tests

| Test | Type | Status |
|---|---|---|
| Expected affected/safe set | Integration | VERIFIED — LOCAL + CLOUD |
| Cleaning excludes later run | Adversarial | VERIFIED — LOCAL + CLOUD |
| Execution requires approval | Authorization | VERIFIED — LOCAL + CLOUD |
| Re-execution creates no effects | Replay | VERIFIED — LOCAL + CLOUD |
| Removing core edge changes result | Graph dependency | VERIFIED — MOCKED |
| Every quarantine has evidence | Invariant | VERIFIED — LOCAL + CLOUD |

Run:

```powershell
python -m unittest discover -s tests -v
npm run check
npm run build
```

## P0 gaps

- Add five more frozen scenarios; current coverage is one scenario with six proof tests.
- Add concurrent replay and partial-failure recovery tests.
- Add API malformed-input and unknown-operator tests.
- Add automated browser accessibility and performance tests.
