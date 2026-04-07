# Architecture

## Recommended V1 Stack

- Frontend: React + TypeScript with Vite
- Backend: FastAPI
- Session/cache: Redis
- Primary database: PostgreSQL with pgvector
- Vector storage: pgvector inside PostgreSQL
- Orchestration: Docker Compose locally, Kubernetes later

## Monorepo Layout

```text
backend/
  app/
  tests/
frontend/
  src/
infra/
  docker-compose.infra.yml
  k8s/
docs/
```

## Service Boundaries

- `frontend`: browser-facing web app, published to a host port
- `backend`: internal API only, reachable from the frontend or internal network
- `postgres`: persistent transactional storage plus vector storage through pgvector
- `redis`: anonymous session storage, cache, optional queue support

## Core Domain Objects

- `AnonymousUser`
  - stable visitor identifier
  - created from session bootstrap
- `Character`
  - owner anonymous user id
  - name
  - power description
  - optional `deleted_at` for soft delete
- `Battle`
  - challenger character id
  - defender character id
  - requested by anonymous user id
  - status
  - winner character id
  - explanation
  - left and right participant snapshots for history rendering
- `BattleJudgment`
  - raw LLM response
  - validated winner
  - prompt version
- `LeaderboardEntry`
  - character id
  - derived score
  - stored in Redis ZSET for ranking reads

## Anonymous Identity Strategy

Recommended v1 approach:

- On the first visit, the frontend calls `POST /api/session/bootstrap`.
- The backend creates an anonymous user record in PostgreSQL with a server-generated UUID.
- The backend creates a random session token and stores it in Redis with the anonymous user id as the value payload.
- The backend sets an `HttpOnly` cookie whose value is the opaque session token.
- All later create/battle requests resolve the anonymous user from that cookie.

Recommended Redis session payload:

- `anonymous_user_id`
- `created_at`
- `last_seen_at`
- optional `session_version`

What not to use as the identity source:

- raw IP address
- user-agent string
- browser fingerprinting

Those signals can be stored separately for abuse monitoring if needed, but they should not be the primary user identity.

Why this fits v1:

- simpler than full auth
- enough to associate users with characters and battle history
- easy to rotate or expire
- confirmed session TTL: 30 days

## Battle Flow

1. Visitor lands on the frontend.
2. Frontend bootstraps anonymous session.
3. Visitor creates a character.
4. Visitor selects two characters for battle.
5. Backend loads both characters and builds a structured judge prompt.
6. Backend sends the prompt to the LLM.
7. Backend validates the result against a strict JSON schema and the battle output contract.
8. If validation fails, the harness retry loop asks the model to correct the output.
9. Backend stores the final judgment and returns the winner to the frontend.

## Realtime Strategy

Recommended v1 rule:

- do not use WebSocket for the battle flow
- do not use SSE for one-shot battle results
- create-battle endpoints should return a `pending` battle record immediately
- the actual LLM judgment should run in a background job with its own database session
- the frontend should poll `GET /api/battles/{battleId}` on a short interval until the battle reaches a terminal state
- refresh leaderboard and public history with normal `GET` requests after ranked battles complete

Why this fits the current product:

- battle results are not token-streamed to the browser
- the user does not need bidirectional communication
- short-lived polling is simpler than keeping realtime connections open
- background execution keeps request latency bounded even when LLM calls are slower

Recommended polling behavior for v1:

- `POST /api/battles/practice` or `POST /api/battles/ranked-random` returns a `pending` battle record with `battleId`
- the frontend polls `GET /api/battles/{battleId}` every 2 seconds until the status is `*_completed` or `*_failed`
- polling stops immediately when the battle reaches a terminal state
- after a successful ranked battle, refetch public history and leaderboard once

## Deletion And History Strategy

- Characters should support soft delete through a nullable `deleted_at` field.
- Soft-deleted characters must disappear from public selection lists.
- Historical battles must continue to reference the original character ids.
- Battle records should store participant snapshots so public history does not depend on live character rows.
- Soft delete is required because battle history is public and should remain auditable.

Practical interpretation of the current rule:

- remove soft-deleted characters from character lookup APIs
- do not rely on active character queries when rendering old battle history

## Leaderboard Strategy

- Public battle history is listed latest-first from PostgreSQL.
- Public ranking is separate from history and served from Redis ZSET.
- Redis ZSET should be treated as a read-optimized projection derived from verified battle outcomes.
- A companion Redis hash may hold last-win timestamps for deterministic tie-breaking.
- PostgreSQL remains the source of truth for battle results.
- If Redis data is lost, the leaderboard must be rebuildable from PostgreSQL.
- Every verified win adds exactly `+1` point.
- Tie-break rule: for equal scores, use recent victory timestamp in ascending order as requested.

## Where Harness Engineering Shows Up

- `AGENTS.md` defines code and behavior constraints.
- Battle rules force a strict winner schema.
- The backend separates prompt building, LLM calling, and validation.
- Validation failure feeds directly into a retry loop before the response reaches the user.
- CI gates can later reject architecture drift such as oversized files or missing tests.
- Jenkins should execute deterministic gates, not replace them with subjective approval.

## Exposure Model

- Publish the frontend to a host port such as `13000`.
- Keep the backend on the internal Docker network only.
- The frontend should call the backend through an internal service name in Compose or through an in-container reverse proxy.
- In Kubernetes, expose only the frontend with a `NodePort` Service and keep the backend as `ClusterIP`.

For local Compose infrastructure:

- PostgreSQL is published on `15432`
- Redis is published on `16379`

## pgvector Guidance

pgvector is the recommended vector approach for this project.

Why it fits:

- the application already needs PostgreSQL
- infrastructure stays simpler than adding a separate vector service
- battle-history similarity search can live next to transactional battle data

Good reasons to use pgvector later in the product flow:

- retrieve similar past battles for more consistent judging
- search character descriptions semantically
- reduce prompt size by selecting only relevant historical battles

For the first release, it is acceptable to enable pgvector and postpone actual embedding-based retrieval until the basic battle loop is stable.

## Frontend-To-Backend Network Pattern

Because the backend is not publicly exposed, browser traffic should not call the backend service directly by cluster DNS name.

Recommended pattern:

- serve the React build through Nginx in the frontend container
- proxy `/api` from Nginx to the internal backend service
- expose only the frontend service through NodePort

## Local Kubernetes VM Cluster Note

Because the cluster runs in local VMs, container images built on the host machine may not be visible inside cluster nodes.

Recommended deployment rule:

- publish images to a registry reachable from the VM nodes, then deploy by tag

Avoid relying on:

- host-local Docker images being automatically available to the cluster
- manual image copying as the long-term CI/CD path

This matters for Jenkins as well. A successful pipeline should publish deployable images to a registry that the cluster can pull from.

## CI/CD Delivery Constraints

- Source control: GitHub
- Jenkins trigger mode: SCM polling
- Image distribution: local registry reachable from VM nodes
- Deployment command: `kubectl apply -k`
