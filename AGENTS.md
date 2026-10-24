# LotLine project instructions

- Read `docs/PROJECT_CONTEXT.md` before lifecycle, architecture, readiness, or submission work. Recover the current branch, HEAD, and working-tree state before continuing.
- Treat `evidence/cloud-demo-run.json` as a retained real FalkorDB Cloud execution, the six-scenario benchmark as a mocked graph-adapter test, and the public Vercel UI as credential-free playback. Never describe playback as a live cloud mutation.
- Keep cloud credentials out of the public build, Git history, logs, and documentation. The credentialed API is localhost-only until authentication and operational safeguards are implemented and verified.
- Record only tests, CI, deploys, and integrations actually verified. Update `docs/PROJECT_CONTEXT.md` after material milestones or blocker changes; do not erase decision history.
- Do not push, deploy, or submit without user authorization. The project is a hackathon demonstrator, not an operational food-safety system.
