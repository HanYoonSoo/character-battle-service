# Engineering Rules

The harness must prefer predictable behavior over clever behavior.

Rules:

- Read context only from the `docs/` directory.
- Validation failure must trigger a retry with the verification error attached.
- A completed run must satisfy the response contract before it is shown to a user.
- Tests are the default gate for behavior changes.
- Frontend changes must pass deterministic dependency installation and a production build.
- Backend changes must update `backend/uv.lock` and pass locked dependency sync, dependency consistency checks, and runtime import verification.
- Simple questions and executable tasks must be routed differently.
- Questions may return an answer only; tasks may enter CI/CD after deterministic gates pass.
- Do not introduce duplicate code when a shared module or class would fit better.
- Do not place the entire application in one file.
- Avoid code that looks detached from real production practice.
- Prefer object-oriented separation when it clarifies responsibility and keeps the code extensible.
- Keep domain logic out of transport handlers and UI components.
- Validate LLM battle output against a strict schema before persisting results.
- Use JSON schema enforcement for GPT-4o responses rather than loose JSON parsing.
- Battle explanations returned by the LLM must be written in Korean.
- Battle explanations may be lightly playful in tone, but should stay readable and product-safe.
- Anonymous-user identification must be stable enough to associate characters and battles across requests.
- The backend should not publish a host port in default local infrastructure.
- Characters with battle history should be soft deleted so historical records stay valid.
- Public leaderboard scores in Redis ZSET must be derived from verified battle outcomes and rebuildable from PostgreSQL.
- Private practice battles must not affect public leaderboard scores.
- Ranked random battles must choose opponents from characters owned by other users.
- Asynchronous battle execution must persist a `pending` battle first and only publish completed ranked battles to the public feed.
- Polling must stop as soon as a battle reaches a terminal state.
- Jenkins jobs and pipelines should be managed as code.
- Deterministic gate failures may enter a bounded auto-repair loop before human escalation.
- Pre-commit and CI gates must block commits when sensitive tokens or private key material are detected.
- Repository hygiene checks should run periodically to detect drift and dead code.
- Repeated deterministic failures should be promoted into stronger tests, validators, or CI gates.

The initial worker may be simple. The harness matters more than model sophistication.
