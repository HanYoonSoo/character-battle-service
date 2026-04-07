# Frontend Structure

Recommended frontend responsibilities:

- bootstrap anonymous session on first load
- allow character creation
- trigger battles
- render battle results and recent history

Suggested feature areas:

- `app/`: router and app shell
- `pages/`: route-level screens
- `features/characters/`
- `features/battles/`
- `features/leaderboard/`
- `features/session/`
- `shared/api/`: HTTP client layer
- `shared/types/`: API-facing view models
- `shared/ui/`: reusable UI blocks

The frontend should be the only service published to a host port by default.

Deployment note:

- the built frontend is intended to run behind Nginx
- Nginx proxies `/api` to the internal backend service
- the Kubernetes Service for the frontend should use `NodePort`

Current implementation notes:

- anonymous session bootstrap runs before the routed app shell renders
- pages are wired to the backend API contract through feature-scoped API modules
- character management supports create, edit, delete, and public browsing flows
- battle creation and public history rendering use the backend snapshot-based battle responses
- leaderboard reads are separated from battle history and rendered independently
- MUI is the shared design system for layout, form controls, navigation, and data display
- the theme lives in `src/app/theme.ts` and is the single source of truth for palette, typography, spacing, and surface styling
- the routed UI is written primarily in Korean
- light and dark mode are both supported and the selected mode is persisted in local storage

## Local Run

Install dependencies and start the Vite development server:

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```

Local API requests use the Vite proxy:

- `/api` is proxied to `http://localhost:8000` by default
- override with `VITE_API_PROXY_TARGET` if the backend runs elsewhere

## Full Docker Compose Run

Bring up the full local stack:

```bash
cd /Users/hanyoonsoo/harness-engineering-playground
cp .env.example .env
OPENAI_API_KEY=your_key_here docker compose up --build -d
```

Host-exposed ports:

- frontend: `13000`
- PostgreSQL: `15432`
- Redis: `16379`

The backend stays on the internal Compose network and is not published to the host by default.
