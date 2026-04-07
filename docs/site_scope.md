# Site Scope

## Site Type

Examples:

- personal portfolio
- landing page for a product
- internal dashboard
- documentation site
- small CRUD app

Current answer:

- Anonymous character battle web service

## Required Pages

- Landing page with service explanation and recent battles
- Character creation page
- Battle page for selecting two characters and requesting a judgment
- Battle result/history page

## Core User Flow

- A visitor enters the site.
- The frontend requests anonymous session bootstrap.
- The visitor creates one or more characters with names and power descriptions.
- The visitor selects two characters for a 1:1 battle.
- The backend builds the battle prompt and sends it to the LLM.
- The backend validates the LLM output and stores exactly one winner.
- The frontend shows the winner, explanation, and battle record.

## Preferred Stack

Examples:

- Python + FastAPI + Jinja
- TypeScript + React + Vite
- Next.js

Current answer:

- React + TypeScript frontend with Vite
- FastAPI backend with a layered service/repository structure
- Docker Compose for local infrastructure, Kubernetes manifests included for local cluster deployment

## Data And Integrations

- Does the site need a database?
- Does it call any external API?
- Does it need authentication?

Current answers:

- Database: PostgreSQL
- Cache/session store: Redis
- Vector store: pgvector inside PostgreSQL
- Authentication: none in v1
- User identification: Redis-backed `HttpOnly` session cookie mapped to a server-generated anonymous user id
- External API: LLM provider for battle judgment

## Design Constraints

- desktop/mobile support
- tone or visual direction
- components you know you want

Current answers:

- Desktop and mobile support
- Simple, game-like visual language
- Shared design system: MUI with a project-level custom theme
- Frontend should be the only host-exposed service by default
- Backend should stay on the internal Docker network or ClusterIP service
- Local Compose host ports should follow the `default + 10000` convention for exposed services
- Local Kubernetes exposure should use a frontend NodePort service only
