# Sponsor Map

## Program

- Hackathon: Graph Hacks: Context for AI Agents.
- Organizer: WeMakeDevs × FalkorDB.
- Primary track: Agents That Act on Connected Data.

## Integration

| Sponsor | Primitive | Load-bearing? | Status | Evidence |
|---|---|---:|---|---|
| FalkorDB | Cypher traversal, persistent case state, evidence, approval, action receipts | Yes | VERIFIED — CLOUD | `evidence/cloud-demo-run.json`, graph `lotline_proof_20261017_002910` |

## Removal test

The local adversarial test proves that deleting `ING-ALM-042 -[:USED_IN]-> RUN-100` removes the direct recall set. The cloud run independently proves that the same fixed Cypher traversals and persistent workflow execute on FalkorDB.

## Verification completed

1. Provisioned FalkorDB Cloud without Docker.
2. Implemented the real repository adapter and fixed Cypher contract.
3. Seeded a fresh, synthetic graph through Cypher.
4. Ran trace → approval → effects → replay on the cloud graph.
5. Captured sanitized machine-readable output and retained the proof graph.

The project may accurately say “powered by FalkorDB” for this verified prototype. It must not imply production certification, real customer data, or regulatory approval.
