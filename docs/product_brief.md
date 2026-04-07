# Product Brief

The starter project is for learning harness engineering by building a character battle website.

The harness should help produce code that looks closer to practical team code than to a one-off tutorial project.

Required response contract:

- Return an answer.
- Include at least one citation when the answer is grounded.
- Return `needs_followup = true` when the documents do not support a safe answer.
- Never invent facts that do not appear in the approved documents.

Initial product direction:

- Build a small website where anonymous users create characters and run 1:1 battles.
- Use the harness to constrain how code is generated and reviewed.
- Prefer maintainable structure, reusable components, and realistic project organization.
- A battle result must always produce exactly one winner.
- Login is not required for v1, but users must still be identifiable through an anonymous session mechanism.
- Infrastructure should support Redis and PostgreSQL with pgvector using Docker first and Kubernetes later.
- The backend should remain internal by default, while the frontend is the only directly exposed service.
- The frontend stack is React + Vite.
- The backend stack is FastAPI with a layered package structure.
- The local Kubernetes entrypoint is a frontend NodePort service only.
- Public battle history is visible to everyone.
- Public ranking is derived from verified battle wins and served from Redis ZSET.
- Character deletion must preserve historical battle integrity through soft delete behavior.
- GPT-4o output must be constrained with JSON schema validation.
- Leaderboard score increments by exactly `+1` per verified win.
- Jenkins should poll GitHub rather than depend on public webhook exposure in the local VM cluster.
- Deployments should apply Kustomize manifests with `kubectl apply -k`.

Still to define:

- Whether embedding-based retrieval is required in v1 or introduced in v2
