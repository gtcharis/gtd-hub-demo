# Demonstrator architecture — v0.2.4

## Frontend
React 18 + TypeScript + Vite + Tailwind CSS. PWA support is provided by `vite-plugin-pwa`. The frontend uses persistent hash-based routes, a shared application shell and a small authentication context. Authenticated user identity and role are loaded from the API; the role selector is no longer an identity mechanism.

## Backend
FastAPI under `/backend`, with SQLAlchemy persistence and Alembic migrations.

- `GET /api/v1/health` — public health check
- `POST /api/v1/auth/login` — authenticate and create a revocable session
- `GET /api/v1/auth/me` — authenticated identity
- `POST /api/v1/auth/logout` — revoke current session
- `GET /api/v1/demo/overview` — authenticated
- `GET /api/v1/demo/mentors` — authenticated
- `GET /api/v1/admin/access-check` — role-restricted example for organisation/programme administrators

## Data and identity
Institutions, users and sessions are persisted in SQLAlchemy models. PostgreSQL is the intended deployed database; SQLite is the no-configuration local development default. Passwords use Argon2 hashes. Session tokens are opaque random values; only SHA-256 token hashes are stored, and sessions expire after eight hours or can be revoked at logout.

## Deployment
- GitHub Pages builds the frontend from the repository root using the configured Vite base `/gtd-hub-demo/`.
- Railway service root directory: `/backend`; Docker startup applies Alembic migrations.
- Configure `DATABASE_URL` and exact `CORS_ORIGINS` values in Railway.
- Run `python -m app.seed_demo_users` once to create the six fictional accounts.

## Scope boundary
This release establishes authentication and identity, not the complete module permission matrix or production safeguarding service. There are no real GBV report intake or operational case-management workflows. All seeded identities and data are fictional.
