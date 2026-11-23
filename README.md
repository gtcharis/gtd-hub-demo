# GTD Hub — Proposal Demonstrator v0.2

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
