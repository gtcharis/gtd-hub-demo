# GTD Hub Demonstrator API

FastAPI scaffold for the proposal demonstrator. This is an API-ready foundation, not the production safeguarding backend.

## Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

- Health: `GET /api/v1/health`
- Demo overview: `GET /api/v1/demo/overview`
- Demo mentors: `GET /api/v1/demo/mentors`
- OpenAPI UI: `/docs`

## Railway

Set the Railway service root directory to `/backend`. Railway will build from `backend/Dockerfile`. Configure `CORS_ORIGINS` with the exact GitHub Pages origin and any local development origin required.

## Deliberate limitations

No authentication, report intake, case persistence, notifications, or real personal data endpoints are implemented. Do not add live GBV submissions to this proposal demonstrator. A production implementation requires approved requirements, threat modelling, consent/safeguarding protocols, separate protected case-data storage, access governance and partner approval.
