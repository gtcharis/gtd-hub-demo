# GTD Hub — Interactive Proposal Demonstrator

A proposal-stage, browser-based product concept for the Gender-Transformative Digital Hub (GTD Hub), supporting the PROGEN-Hub for STEM programme.

## Important demonstration boundary

This is **not a production system, a live reporting channel, or a safeguarding service**. All users, institutions, mentors, discussions, cases and metrics are fictional. The reporting journey is simulated entirely in the browser. It does not transmit, store or notify anyone about a real report. Do not enter real personal information or real experiences.

## Technology

- React + Vite + TypeScript
- Lucide icons
- Local, fictional demonstration data
- No production backend or authentication

## Run locally

```bash
npm install
npm run dev
```

## Build

```bash
npm run build
npm run preview
```

## GitHub Pages deployment

The Vite `base` in `vite.config.ts` is currently `/gtd-hub-demo/`. If the GitHub repository has a different name, update this value to `/<repository-name>/` before building. For a user/organisation site repository named `<owner>.github.io`, use `/`.

1. Create a GitHub repository named `gtd-hub-demo` (or update the Vite base to match your repository name).
2. Push this project to the repository.
3. In GitHub, open **Settings → Pages** and select **GitHub Actions** as the build/deployment source.
4. Add `.github/workflows/deploy.yml` from this project (provided below in the repository after setup), or use the included workflow if present.
5. Push to `main`; GitHub Actions builds and publishes `dist/`.

## Product areas demonstrated

1. Student/staff overview and support discovery
2. Safe and anonymous reporting journey (fictional simulation)
3. Mentorship discovery and sample connection requests
4. Peer community and learning library
5. Case-handler workspace with fictional records and simulated status changes
6. HEI and central programme dashboards with illustrative aggregate metrics
7. Role switching for six demonstration personas

## Production architecture proposed separately

React/Vite/TypeScript PWA → FastAPI → Pydantic schemas → SQLAlchemy → PostgreSQL, with Alembic migrations and OpenAPI/Swagger documentation. The production solution will require approved identity/access controls, institution-scoped authorisation, separate protected GBV case-data storage, partner-controlled encryption keys, audit logging, integrations, security testing and partner-owned infrastructure/accounts.

## Before external sharing

- Confirm the public GitHub repository name and adjust `base` in `vite.config.ts`.
- Review all wording with the project partners before treating any content as approved institutional policy.
- Keep the prototype disclaimer visible.
- Do not add real reports, contact details, case records or participant information.
