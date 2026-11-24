# GTD Hub Demonstrator API — v0.2.4

FastAPI authentication and identity foundation for the proposal demonstrator. All seeded identities and records are fictional.

## Local setup (Windows PowerShell)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

For quick local development, the backend defaults to SQLite (`gtdhub_demo.db`). For PostgreSQL, create a database named `gtdhub_demo`, copy `.env.example` values into your environment, and set `DATABASE_URL` to your PostgreSQL connection string. The PostgreSQL driver is psycopg 3.

Apply migrations and seed the six fictional role accounts:

```powershell
alembic upgrade head
python -m app.seed_demo_users
```

Start the API:

```powershell
python -m uvicorn app.main:app --reload
```

API documentation: `http://127.0.0.1:8000/docs`

## Demonstration accounts

All six accounts use the value of `DEMO_DEFAULT_PASSWORD` at the time they are first seeded. The default for local demonstration is `GtdHubDemo!2026`.

| Role | Email |
|---|---|
| Member | `member@gtdhub.demo` |
| Mentor | `mentor@gtdhub.demo` |
| Moderator | `moderator@gtdhub.demo` |
| Case Handler | `casehandler@gtdhub.demo` |
| Organisation Administrator | `orgadmin@gtdhub.demo` |
| Programme Administrator | `programmeadmin@gtdhub.demo` |

The seed command is idempotent and does not overwrite existing users or passwords. If you change `DEMO_DEFAULT_PASSWORD` after seeding, existing accounts retain their existing password.

## Authentication API

- `POST /api/v1/auth/login` — validates credentials and creates a revocable eight-hour session.
- `GET /api/v1/auth/me` — returns the authenticated user's identity, role and institution.
- `POST /api/v1/auth/logout` — revokes the current session.
- `GET /api/v1/health` — public health check.
- `GET /api/v1/demo/overview` — authenticated.
- `GET /api/v1/demo/mentors` — authenticated.

Protected endpoints require `Authorization: Bearer <access_token>`. Session tokens are random opaque values; only SHA-256 token hashes are stored in the database. Passwords are hashed using Argon2.

## Frontend configuration

In the frontend project root, create `.env.local`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Restart Vite after changing environment variables.

## Railway

Set the service root directory to `/backend`. Add a PostgreSQL service and set `DATABASE_URL` to its connection string. Configure `CORS_ORIGINS` with the exact frontend origin. The container runs `alembic upgrade head` before starting Uvicorn. Run `python -m app.seed_demo_users` once through the Railway shell to create the initial demo accounts.

## Demonstrator security boundary

This is a functional proposal demonstrator, not a production safeguarding service. Tokens are held by the browser frontend to support the separate GitHub Pages and API origins. Before production, move to a reviewed secure session architecture (preferably HttpOnly secure cookies or an approved identity provider), add rate limiting, password reset and account lifecycle workflows, secrets management, audit controls, threat modelling and independent security testing. Do not enter real GBV disclosures or sensitive personal data.
