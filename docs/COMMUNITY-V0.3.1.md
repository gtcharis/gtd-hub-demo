# GTD Hub v0.3.1 — Community workflow

## Scope
- Institution-scoped discussion listing and search.
- Create discussions and replies.
- Authors can edit their own discussions and replies.
- Moderators can lock, reopen or hide discussions and hide replies.
- Programme Administrators can moderate across institutions.
- Hidden discussions and replies are excluded from normal community views.

## API
- `GET /api/v1/community/discussions?q=&category=`
- `POST /api/v1/community/discussions`
- `PATCH /api/v1/community/discussions/{id}`
- `POST /api/v1/community/discussions/{id}/replies`
- `PATCH /api/v1/community/replies/{id}`
- `PATCH /api/v1/community/discussions/{id}/moderation`
- `PATCH /api/v1/community/replies/{id}/moderation`

## Safety
This is a fictional demonstrator. Do not enter real personal, safeguarding or GBV disclosures. Community content is institution-scoped; moderation is permission-controlled.

## Migration
Apply with `python -m alembic upgrade head`. New tables: `community_discussions`, `community_replies`.
