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
| Six safety-policy scenarios | Adversarial matrix | VERIFIED — MOCKED |

Run:

```powershell
python -m unittest discover -s tests -v
python scenario_benchmark.py --write
npm run check
npm run build
```

## P0 gaps

- Demo video is not yet recorded or linked.

## P1 gaps

- Add concurrent replay and partial-failure recovery tests before exposing mutations publicly.
- Add API malformed-input and unknown-operator HTTP tests.

## P2 gaps

- Add automated browser accessibility and performance tests.
