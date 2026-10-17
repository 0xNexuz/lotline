# Security

## Supported scope

LotLine is a hackathon-grade, synthetic-data proof. The public Vercel site is a static, read-only playback of a verified FalkorDB Cloud run. It does not expose database credentials or mutation endpoints.

The Python cloud API is intended for local operator-controlled demos only. It binds to `127.0.0.1` and must not be exposed publicly without authentication, authorization, rate limiting, audit logging, concurrency controls, and a secrets manager.

## Reporting

Please open a private security advisory in the GitHub repository rather than publishing credential or vulnerability details in an issue.

## Known boundaries

- All Northstar Foods records are synthetic.
- Quarantine and notification effects modify only synthetic graph state.
- LotLine does not validate upstream record truth or provide regulatory compliance.
- The current cloud proof does not establish concurrent-execution safety across multiple API processes.
