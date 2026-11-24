# GTD Hub — Proposal Demonstrator v0.2.3

A mobile-first, responsive and installable PWA concept for the GTD Hub selection-stage technical proposal.

## Important boundary

This is a proposal-stage interactive demonstrator, not the full contracted GTD Hub system. It uses fictional identities, organisations, metrics, activities and cases. It is not a live GBV reporting channel, does not transmit reports, and must not be used to enter real personal information or experiences.

## Stack

- React 18 + TypeScript + Vite
- Tailwind CSS 3
- Lucide React
- `vite-plugin-pwa` service worker and manifest
- FastAPI read-only demonstration API scaffold
- API-ready frontend client with local fictional-data fallback

## Run frontend

```bash
npm install
npm run dev
```

Build:
```bash
npm run typecheck
npm run build
npm run preview
```

## Run backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

API docs: `http://localhost:8000/docs`

Set `VITE_API_BASE_URL=http://localhost:8000` in a local `.env` file to configure the frontend API origin. The current UI uses local demo data unless API-backed loading is explicitly wired into a view.

## Deploy

### GitHub Pages
The workflow `.github/workflows/deploy.yml` builds and deploys the frontend. Vite base and PWA scope are configured for `/gtd-hub-demo/`. Set GitHub Pages source to GitHub Actions.

### Railway
Create a Railway service from the same repository and set its root directory to `/backend`. It will use `backend/Dockerfile`. Configure `CORS_ORIGINS` with the exact frontend origin, e.g. `https://gtcharis.github.io`.

## Documentation

- `docs/ui/SCREEN-INVENTORY.md` — demonstrator screen register
- `docs/architecture/OVERVIEW.md` — frontend/API/deployment architecture
- `docs/security/SECURITY-AND-ACCESSIBILITY.md` — security and WCAG design/test boundaries
- `backend/README.md` — API and Railway instructions

## Validation status

This archive was generated from the supplied v0.1 source and restructured. Dependency installation and production build have not been run in this environment. Run `npm install`, `npm run typecheck`, and `npm run build` locally before pushing. Backend tests can be run with `pytest` from `backend/` after installing `requirements-dev.txt`.


## v0.2.2 frontend foundation update

- Frontend entry and application shell now live under `src/app/`.
- Added persistent hash-based screen routing. URLs such as `/#/mentorship` survive refresh and work on GitHub Pages without server rewrite configuration.
- Added page-level entry modules under `src/pages/` while retaining existing screen implementations in `ScreenComponents.tsx` to preserve current behaviour during the staged extraction.
- Moved the API client into `src/services/api.ts`; `src/lib/api.ts` remains as a compatibility re-export.
- Moved global styles into `src/styles/styles.css`.
- Added supplied GTD Hub brand assets under `public/brand/` and integrated the teal horizontal logo into the shared brand component.
- Added common component and layout directories as the next extraction boundaries.

The backend remains at the repository root in `/backend`. Authentication, persistent database records and write-enabled workflows are the next implementation phase; they are not represented as completed in this update.


## v0.2.3 application foundation update

- Added a reusable `src/components/layout/Footer.tsx` component.
- Replaced the footer's plain-text partner identity with the combined PROGEN-Hub for STEM and GTD Hub graphic.
- Added responsive footer logo sizing for mobile and desktop layouts.
- Retained the existing hash-based routing under `src/app/router.tsx`. Routes such as `/#/mentorship` remain refresh-safe and compatible with GitHub Pages.
- Kept the existing page implementations and backend API integration intact to avoid a disruptive rewrite.
- Bumped the frontend package version to `0.2.3`.
- Removed local environment files, Python virtual environments, generated build output and audit reports from this source archive.

### Verification

The supplied v0.2.2 baseline was previously confirmed by the developer to pass `npm run typecheck` and `npm run build` after correcting the `DownloadIcon` import. The v0.2.3 source changes have not yet been run through a fresh dependency install and production build in this packaging environment. Run the commands below after extraction:

```bash
npm ci
npm run typecheck
npm run build
```

The backend remains the existing read-only FastAPI scaffold. Authentication, PostgreSQL persistence, role enforcement and write-enabled module workflows are not included in this release.
