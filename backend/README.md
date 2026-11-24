# GTD Hub API — v0.2.5

FastAPI API for the GTD Hub proposal demonstrator. Demonstration records are fictional.

## Database

PostgreSQL is required. SQLite is not supported.

Set `DATABASE_URL` to a PostgreSQL connection URL using the psycopg driver:

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE
```

Run migrations from the `backend` directory:

```powershell
python -m alembic upgrade head
```

## Run locally

```powershell
python -m uvicorn app.main:app --reload
```

## Demo users

Set `DEMO_DEFAULT_PASSWORD` before running:

```powershell
python -m app.seed_demo_users
```

The seed script creates missing fictional demo users; it does not reset passwords for existing accounts.

## Tests

Tests require a dedicated PostgreSQL database. Never point `TEST_DATABASE_URL` at production.

```powershell
$env:TEST_DATABASE_URL="postgresql+psycopg://USER:PASSWORD@localhost:5432/gtdhub_test"
python -m pytest
```

The test fixture drops and recreates tables in the configured test database.

## RBAC policy

Role permissions are centralised in `app/role_policy.py`.

- Organisation Administrators are scoped to their own institution.
- Programme Administrators have full programme-wide access across all institutions.
- All protected API endpoints enforce permissions on the server.
- Frontend navigation is not a security boundary.

## Deployment

Railway should use `/backend` as the service root directory and the included Dockerfile. The Dockerfile applies Alembic migrations before starting Uvicorn.
