# GTD Hub v0.3.4 — Learning Library

## Scope

- Replaces the static illustrative Learning cards with a database-backed catalogue.
- Supports private document uploads (PDF, DOCX, PPTX; maximum 10 MB) and external HTTPS links.
- New resources are drafts. Authorised administrators can publish, unpublish or archive them.
- Provides category and keyword search, resource access and a basic audit record.
- Programme Administrators can manage programme-wide or institution-scoped resources. Organisation Administrators are limited to their own institution. Members, Mentors and Moderators can read published programme-wide and own-institution resources.
- Case Handler role is not granted Learning Library access by this release.

## Supabase Storage configuration

Configure these variables in `backend/.env` for local development and in the Railway `gtd_hub_api` service for production:

```dotenv
SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
SUPABASE_SERVICE_ROLE_KEY=YOUR_SERVER_SIDE_SECRET_KEY
SUPABASE_STORAGE_BUCKET=gtdhub-learning-resources
```

The bucket must remain **private** and allow:

- `application/pdf`
- `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- `application/vnd.openxmlformats-officedocument.presentationml.presentation`

Never place `SUPABASE_SERVICE_ROLE_KEY` in a frontend variable or commit it. The API creates five-minute signed URLs after checking the authenticated user's permissions and institution scope.

## Migration and deployment

```powershell
cd backend
alembic upgrade head
```

Then restart the API and build the frontend:

```powershell
cd ..
npm run build
```

## Important limitations

- This release is a functional Learning Library foundation, not a complete TOR/security acceptance. Partner approval is still required for official learning materials, referral content and service contacts.
- Upload only approved learning documents. Never upload GBV case records, participant disclosures or identifiable safeguarding information.
- Learning resource actions are recorded in a SHA-256 hash-chained audit sequence. A dedicated audit verification endpoint and operational review procedure remain future hardening tasks.
- No server-side URL preview or URL fetching is performed.
- Validate the Railway Supabase connection and signed-document access after deployment before enabling production uploads.
