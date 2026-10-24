# Submission Map

## Event

- Name: Graph Hacks: Context for AI Agents.
- Organizer: WeMakeDevs × FalkorDB.
- Official URL: https://www.wemakedevs.org/hackathons/falkordb
- Primary track: Agents That Act on Connected Data.
- Deadline: October 18, 2026, 11:59 PM IST (7:29 PM Africa/Lagos).

Official judging criteria: six equally weighted categories — graph-native FalkorDB use, agent effectiveness, potential impact, technical excellence, explainability/provenance, and creativity/presentation.

Official rules checked: https://www.wemakedevs.org/hackathons/falkordb/rules

## Requirements

| Requirement | Status | Action |
|---|---|---|
| Public repository | COMPLETE | https://github.com/0xNexuz/lotline |
| README + graph model | COMPLETE | Runtime labels, graph model, setup, and non-claims documented |
| Essential Cypher | COMPLETE | Fixed queries verified on retained FalkorDB Cloud graph |
| Demo video | NOT IMPLEMENTED | Record the 90-second verified flow |
| Live app or complete local setup | COMPLETE | https://lotline-ai.vercel.app; updated production browser flow and receipt verified 2026-10-24 |
| FalkorDB central integration | VERIFIED | `evidence/cloud-demo-run.json` |
| Track named | COMPLETE | Track 01 |
| AI assistance disclosure | COMPLETE | README |
| Registration | UNVERIFIED | User must confirm |
| Submission | NOT IMPLEMENTED | Do only after review |

## Submission form answers

### Project title

LotLine

### Description

Food recall teams must trace a flagged ingredient across production runs, shared equipment, cleaning events, shipments, and stores without recalling unrelated inventory. LotLine is a deterministic, graph-native safety agent that uses FalkorDB to find direct and cross-contact exposure, explains every affected lot, stops at validated cleanings, and requires human approval before recording idempotent actions.

### Track

Agents That Act on Connected Data

### Repository

https://github.com/0xNexuz/lotline

### Demo video

**REQUIRED — add the public or unlisted YouTube URL after recording.**

### Live demo or deployment

https://lotline-ai.vercel.app

### How did you use FalkorDB in your project?

FalkorDB is LotLine's load-bearing reasoning surface. An alert is connected to an ingredient lot, production runs, lines, cleaning events, product lots, shipments, and destinations. Fixed Cypher traversals find direct lineage and later runs on the same line inside a 60-minute policy window, while a validated cleaning relationship stops propagation. LotLine stores the recall case, evidence paths, proposed actions, operator approvals, and idempotent effects in the graph. Removing the core `USED_IN` relationship changes the decision, which is covered by a regression test. The retained real-cloud run found three affected lots, spared seven, created five effects after approval, and created zero new effects when replayed.

### Blog link

Optional. Leave blank unless a public technical article is published before submission.

### What did you like about FalkorDB?

FalkorDB made the reasoning path inspectable instead of hiding it in application joins. The same graph can represent lineage, production adjacency, cleaning boundaries, distribution, approval, and execution evidence, and Cypher expresses the multi-hop safety question directly. FalkorDB Cloud also made it practical to verify the complete workflow without operating local database infrastructure.

### What improvements would you like to see in FalkorDB?

For safety-critical agent workflows, first-class examples for least-privilege credentials, read-only versus write roles, idempotent mutation patterns, and managed audit exports would make production hardening easier. A lightweight browser embeddable view for a parameterized evidence path would also help teams explain graph-backed decisions without exposing database credentials.

## Judge path

Problem → alert → graph evidence → cleaning exception → approval → actions → replay proof → FalkorDB removal test.

## Submission gate

Final status: **NOT SUBMITTED — VIDEO AND REGISTRATION CONFIRMATION OUTSTANDING; PUBLISHED DEADLINE PASSED**
Conservative score: **90/100**

P0 still owned by the participant: demo video and registration/form availability
confirmation with the organizers. Official submissions closed October 18, 2026
at 11:59 PM IST, so a late entry must not be assumed possible. The public
repository and production URL are complete.
The six-scenario benchmark is complete. Operational hardening remains explicitly
out of scope for the public credential-free demonstrator.
