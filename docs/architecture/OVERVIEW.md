# Demonstrator architecture

## Frontend
React + TypeScript + Vite + Tailwind CSS. PWA support is provided by `vite-plugin-pwa` with auto-update registration and a web app manifest.

## Backend
FastAPI scaffold under `/backend`, exposing versioned read-only demonstration endpoints:
- `GET /api/v1/health`
- `GET /api/v1/demo/overview`
- `GET /api/v1/demo/mentors`

The frontend API client is in `src/lib/api.ts`. Set `VITE_API_BASE_URL` to the deployed backend origin. If unset or unavailable, the current UI continues to use local fictional demonstration data.

## Deployment
- GitHub Pages builds the frontend from the repository root using `vite.config.ts` base `/gtd-hub-demo/`.
- Railway service root directory: `/backend`; Dockerfile deployment.
- Configure exact CORS origins in Railway.

## Production boundary
The demonstrator API is read-only and contains no GBV report intake or case write endpoints. PostgreSQL, production authentication, organisation-scoped authorisation, case-data separation, consent records, audit events, integrations and operational controls remain production design/build tasks after partner-approved requirements.
