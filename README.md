# GTD Hub — Gender-Transformative Digital Hub

**Current demonstrator baseline: v0.3.5 — Administration, Institutional Insights & M&E**

A mobile-first, responsive and installable Progressive Web Application (PWA) demonstrator for the Gender-Transformative Digital Hub (GTD Hub), supporting the PROGEN-Hub for STEM programme.

---

## 1. Demonstrator Boundary

The application uses fictional identities, institutions, accounts and records.

**This is not a live GBV reporting channel.** It must not be used to submit real personal information, disclosures, safeguarding cases or confidential institutional records.

The platform demonstrates digital workflows and technical capabilities. Safeguarding triage, referrals, escalation, case decisions and closure remain the responsibility of authorised human personnel.

All support-directory entries and demonstration scenarios must be treated as illustrative unless verified and approved by FAWEZI, BUSE and the relevant participating institutions.

The demonstrator is intended to support technical evaluation, workflow demonstration and further product development. It does not, by itself, establish operational readiness or formal compliance with the programme's security and safeguarding requirements.

## 2. Technology Stack

### Frontend

- React 18
- TypeScript
- Vite
- Tailwind CSS
- Lucide React
- Progressive Web Application functionality via `vite-plugin-pwa`

### Backend

- Python FastAPI
- SQLAlchemy
- Alembic database migrations
- PostgreSQL
- Argon2 password hashing
- Revocable opaque bearer-token sessions

### File storage

- Supabase Storage
- Private `gtdhub-learning-resources` bucket
- Backend-authorised, short-lived signed access URLs
- PostgreSQL stores resource metadata; binary documents are stored separately.

**PostgreSQL is required for all environments and tests. SQLite is not supported.**

## 3. Demonstrator Capabilities

### v0.2.4 — Authentication Foundation

- Institutions, users and revocable login sessions.
- Argon2 password hashing.
- Login, current-user and logout endpoints.
- Six fictional demonstration role accounts.
- Authenticated access to demonstration overview and mentor APIs.
- Role-aware frontend navigation and role-specific landing destinations.
- Login session restoration on refresh.

### v0.2.5 — RBAC Foundation

- Role-based access control foundation.
- Permission-aware navigation and backend authorisation.
- Institutional access boundaries.
- Role-specific capabilities and access restrictions.

### v0.3.0 — Mentorship

- Mentor directory and profiles.
- Mentorship discovery and profile presentation.
- Role-aware mentorship access.
- Demonstration mentor records.

### v0.3.1 — Community

- Community functionality and associated role-aware access.
- Demonstration community experience.

### v0.3.2 — Support, Safe Reporting and Secure Case Data

**Support directory**

- Psychosocial Support.
- Health Services.
- Legal Information and Assistance.
- Institutional Support.
- Peer Support and Mentorship.
- Searchable support information and expandable service details.

**Safe reporting**

- Submission of predefined synthetic scenarios.
- Anonymous and identified demonstration modes.
- Submission receipts.
- Recorded consent and withdrawal functionality.
- Encrypted case payload persistence.

**Secure case data**

- AES-256-GCM authenticated encryption.
- Unique 96-bit nonces.
- Associated data binding encrypted payloads to case references, institutions and schema versions.
- HMAC-SHA-256 audit hash chain.
- Minimal audit metadata rather than plaintext narratives or contact details.
- PostgreSQL transaction advisory locking for audit-chain appends.

The demonstrator does not accept free-text GBV narratives or real contact details.

### v0.3.3 — Full Case Management

Extends the encrypted reporting foundation with:

- Institution-scoped case queues.
- Case Handler assignment.
- Assignment history.
- Human-validated workflow transitions.
- Human-set case priority.
- Encrypted structured case activity notes.
- Case audit inspection.
- Programme-level and institution-level access boundaries.
- Referral workflow gating based on recorded consent.

The system does not automatically assess risk, make safeguarding decisions, send external referrals or issue emergency notifications.

### v0.3.4 — Learning Library

Introduces a central learning-resource catalogue supporting:

- Learning categories.
- Resource search and discovery.
- Resource details and metadata.
- Uploaded documents.
- External learning-resource links.
- Draft, published and archived resource states.
- Resource administration and permission-controlled management.
- Programme-wide and institution-scoped resource visibility.
- Private Supabase Storage for uploaded documents.
- Backend-authorised document access.

Initial supported document formats:

- PDF
- DOCX
- PPTX

Maximum configured upload size: 10 MB.

The Learning Library is intended for approved educational and gender-transformative learning materials. It must not be used to store GBV case records or confidential participant information.

### Demonstration Login Experience

The sign-in screen includes a public Demonstration Accounts panel.

It provides:

- Six role-labelled fictional accounts.
- One shared demonstration password.
- Account selection to populate the sign-in form.
- Password visibility and copy controls.

The panel is intended for proposal evaluation and demonstrator access. It must only be enabled where the accounts contain synthetic data and have appropriately limited permissions.

---

## 4. Post-Proposal Submission Demonstrator Enhancements

**Important distinction:** The following enhancements were implemented after the original consultancy proposal submission. They represent additional product development and improvements to the proposal demonstrator. They should not be interpreted as features promised in, or included in the original proposal submission.

### v0.3.4 — Learning Library enhancement

- Learning catalogue with categories, search and resource metadata.
- Support for approved document uploads and external learning links.
- Draft, published and archived resource states.
- Private Supabase Storage with backend-authorised access.

### v0.3.5 — Administration, Institutional Insights and M&E

Introduces a dedicated administration and programme-monitoring experience.

**Administrative dashboard**

- Live summary counts based on available demonstrator database records.
- Account and active-account statistics.
- Institution counts within the administrator's authorised scope.
- Mentorship and published learning-resource indicators.

**User and role management**

- User account creation.
- User listing and search.
- Role assignment and updates.
- Account activation and deactivation.
- Institution assignment within authorised administrative scope.
- Session revocation following relevant account-access changes.

**Institution management**

- Institution creation.
- Institution details and status management.
- Institution activation and deactivation.
- Programme Administrator oversight across institutions.

**Administrative access boundaries**

- Organisation Administrators are restricted to their own institution.
- Programme Administrators have programme-wide administrative access.
- Ordinary users cannot access administrative endpoints.
- User and institution changes are subject to backend authorisation and validation.

**Administrative audit trail**

- Visibility of recorded administrative events.
- Actor, action, target, timestamp and institution context.
- Recording of administrative actions such as report exports and account or institution management activities.

**Institutional insights and M&E**

- De-identified aggregate indicators.
- Registered and active account counts.
- Mentorship indicators.
- Community activity indicators.
- Published learning-resource indicators.
- Programme-wide or institution-scoped views, according to the administrator's permissions.
- CSV export for further M&E review.

**Small-cell suppression**

The M&E implementation applies an initial small-cell suppression threshold of five:

- Counts below five, including zero, are suppressed.
- Counts of five or more may be displayed.
- Suppressed CSV values are labelled rather than exported as small numerical counts.
- The same suppression principle is applied to the relevant insight and export outputs.

The threshold is an initial demonstrator safeguard. It must be reviewed and formally approved by FAWEZI and BUSE before operational M&E use. Suppression alone does not guarantee anonymity, particularly where datasets can be combined or repeatedly queried.

**Safeguarding and M&E boundaries**

- GBV narratives are excluded from insights and M&E exports.
- Identifiable case-level information and contact details are excluded.
- Administrative statistics are not safeguarding risk scores.
- The indicators describe records currently available in the demonstrator.
- They do not measure participant outcomes, wellbeing, institutional change or programme impact.
- Safeguarding decisions remain with authorised human personnel.

### v0.3.5 Release Verification

The local release verification recorded:

| Verification | Result |
|---|---|
| Backend Python compilation | Passed |
| Backend automated tests | 58 passed |
| Frontend TypeScript/Vite production build | Passed |
| PWA asset generation | Passed |
| Git staged-diff whitespace check | Passed |

The backend test run reported one non-blocking Starlette/AnyIO deprecation warning.

The v0.3.5 implementation was committed and pushed to `main`.

**Release commit:** `fc14de3` — `feat: release GTD Hub v0.3.5 administration and M&E`

The administration and programme-insights interfaces were also checked in the local and hosted demonstrator environments.

### Known deferred issue

The v0.3.4 learning-resource deletion interface has a known delayed-refresh behaviour: a deleted resource may remain visible until the page is refreshed. This was deferred for a later correction and is not represented as fixed in v0.3.5.

---

## 5. Demonstration Accounts

Shared demonstration password:

`ChangeThisDemoPassword!`

| Role | Email |
|---|---|
| Member | `member@gtdhub.demo` |
| Mentor | `mentor@gtdhub.demo` |
| Moderator | `moderator@gtdhub.demo` |
| Case Handler | `casehandler@gtdhub.demo` |
| Organisation Administrator | `orgadmin@gtdhub.demo` |
| Programme Administrator | `programmeadmin@gtdhub.demo` |

These are fictional demonstration accounts. The password must not be reused for real accounts or production staff accounts.

For local initial seeding, configure `DEMO_DEFAULT_PASSWORD` before running the seed command. The seed command does not reset existing accounts. Existing account credentials must be verified separately.

---

## 6. Local Development Setup

### Prerequisites

- Node.js and npm.
- Python.
- PostgreSQL.
- Git.

### Frontend setup

From the repository root:

```powershell
npm ci
```

Create `.env.local`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Start the frontend:

```powershell
npm run dev
```

Run verification:

```powershell
npm run typecheck
npm run build
```

### Backend setup

Open a second PowerShell terminal:

```powershell
cd backend

python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements-dev.txt
```

Configure `backend/.env` using `backend/.env.example` as a reference.

Configure `DATABASE_URL` to a dedicated PostgreSQL database.

Apply migrations:

```powershell
alembic upgrade head
```

Seed demonstration accounts when required:

```powershell
python -m app.seed_demo_users
```

Start the API:

```powershell
python -m uvicorn app.main:app --reload
```

Local API documentation:

`http://127.0.0.1:8000/docs`

### Backend tests

Use a dedicated PostgreSQL test database:

```powershell
$env:TEST_DATABASE_URL = "postgresql+psycopg://.../gtdhub_test"
python -m pytest -q
```

The test database must be separate from production. Never point test fixtures at the production database.

---

## 7. Environment Configuration and Secrets

### Backend configuration

Configure the following through local backend environment variables or the backend hosting provider:

- `DATABASE_URL`
- `CASE_ENCRYPTION_KEY`
- `CASE_ENCRYPTION_KEY_VERSION`
- `CASE_AUDIT_HMAC_KEY`
- `REQUIRE_HTTPS`
- `CORS_ORIGINS`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_STORAGE_BUCKET`

The Supabase configuration uses:

```env
SUPABASE_URL=https://<your-project-ref>.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<server-side-secret-key>
SUPABASE_STORAGE_BUCKET=gtdhub-learning-resources
```

The Supabase secret key must remain server-side. Never place it in frontend environment variables, source code, documentation, ZIP archives or GitHub commits.

### Case encryption and audit keys

The following are separate, independently generated 32-byte secrets:

- `CASE_ENCRYPTION_KEY`: AES-256-GCM encryption key.
- `CASE_AUDIT_HMAC_KEY`: HMAC-SHA-256 audit-chain key.

Generate each independently:

```powershell
python -c "import secrets,base64; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip('='))"
```

Run twice, storing the outputs securely in the appropriate environment variables.

Maintain partner-controlled recovery copies and document key rotation and recovery procedures before any operational data is introduced.

Missing or invalid cryptographic configuration must cause relevant case operations to fail closed.

### Secret management rules

- Never commit `.env`, `.env.local` or other environment files containing actual secrets.
- Never put backend secrets in frontend code.
- Never include actual credentials in release ZIP files.
- Use Railway Variables for hosted backend secrets.
- Rotate compromised credentials immediately.
- Keep independent backups of encryption and audit keys under approved partner-controlled arrangements.

---

## 8. Hosting and Deployment Architecture

The current demonstrator uses three principal hosting components.

### Frontend — GitHub Pages

Live application:

https://gtcharis.github.io/gtd-hub-demo/

Source repository:

https://github.com/gtcharis/gtd-hub-demo

The GitHub Actions workflow `.github/workflows/deploy.yml` builds and deploys the frontend under `/gtd-hub-demo/`.

Configure the GitHub Actions build variable:

```env
VITE_API_BASE_URL=https://gtdhubapi-production.up.railway.app
```

### Backend — Railway

Production API:

https://gtdhubapi-production.up.railway.app

Swagger documentation:

https://gtdhubapi-production.up.railway.app/docs

Railway service:

- Service: `gtd_hub_api`
- Root directory: `/backend`
- PostgreSQL database attached.
- Backend secrets configured through Railway Variables.
- Database migrations applied through Alembic.

Configure `CORS_ORIGINS` to include:

`https://gtcharis.github.io`

### Learning documents — Supabase Storage

- Private storage bucket: `gtdhub-learning-resources`.
- Resource metadata is maintained in Railway PostgreSQL.
- Document binaries are stored in Supabase Storage.
- The backend uses its server-side Supabase secret key to authorise storage operations.
- Short-lived signed URLs are used for authorised document access.

The Supabase project region and data-location arrangements must be assessed and approved by the project partners before any real participant or sensitive operational data is stored.

### Production topology

```text
User browser / installed PWA
          |
          v
GitHub Pages
React + Vite + TypeScript
          |
          | HTTPS API requests
          v
Railway
FastAPI application
          |
          +------ PostgreSQL
          |       Users, roles, cases,
          |       audit records, resources
          |
          +------ Supabase Storage
                  Private learning documents
```

---

## 9. API Documentation

The backend exposes OpenAPI documentation through FastAPI Swagger UI.

Production:

https://gtdhubapi-production.up.railway.app/docs

Local:

http://127.0.0.1:8000/docs

The API includes authentication, mentorship, community, support, secure case management, Learning Library and administration functionality.

API documentation is a demonstrator interface and does not replace formal API specifications, security testing or operational documentation.

---

## 10. Security and Safeguarding Boundaries

The demonstrator includes several security foundations:

- Argon2 password hashing.
- Revocable opaque bearer sessions.
- Role-based access control.
- Institution-scoped access restrictions.
- AES-256-GCM encrypted case payloads.
- HMAC-based tamper-evident audit events.
- Recorded consent and referral gating.
- Private learning-document storage.
- Backend-controlled storage access.
- Administrative audit events.
- Session revocation following relevant administrative access changes.
- De-identified aggregate reporting with small-cell suppression.
- Synthetic demonstration data.

### Outstanding production requirements

The demonstrator is not certified as production-ready or formally security-compliant.

Before operational deployment, the programme partners must address:

- MFA for all staff and administrator accounts.
- Production session architecture and hardening.
- Rate limiting and account recovery.
- Independent OWASP Top 10 and ASVS security testing.
- Critical and high-risk vulnerability remediation.
- TLS and encrypted-backup verification.
- Partner-controlled encryption-key custody, recovery and rotation.
- Approved data-retention and deletion policies.
- Incident response and breach-notification procedures.
- Approved safeguarding protocols and institutional responsibilities.
- Verified support and referral contacts.
- Emergency escalation arrangements and response times.
- Accessibility testing against WCAG 2.1 AA.
- Hosting, data-residency and cross-border processing review.
- Formal approval of the M&E suppression threshold and reporting rules.
- Review of the separate October 2026 developer Technical Paper referenced by the TOR.

The platform records and supports human-led workflows. It does not replace institutional GBV case-management procedures or professional safeguarding judgement.

---

## 11. Development and Release Discipline

Recommended development sequence:

1. Inspect the current baseline.
2. Define release scope and migration impact.
3. Implement backend and frontend changes.
4. Apply migrations locally.
5. Run backend tests against PostgreSQL.
6. Run frontend typecheck and production build.
7. Conduct browser-based role and workflow testing.
8. Review security-sensitive changes.
9. Inspect Git status and confirm secrets are excluded.
10. Commit and push only after verification.
11. Deploy the backend and frontend independently.
12. Perform production smoke tests.

Do not include `.env`, `.venv`, `node_modules`, `dist`, caches, local databases or secret-bearing archives in source-control commits or release packages.

---

## 12. Repository Structure

```text
gtd-hub-demo/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── models.py
│   │   ├── role_policy.py
│   │   ├── learning_storage.py
│   │   └── main.py
│   ├── migrations/
│   │   └── versions/
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── docs/
│   ├── releases/
│   ├── architecture/
│   └── GTD-HUB-v0.3.4-LEARNING-LIBRARY.md
├── public/
├── src/
│   ├── app/
│   ├── features/
│   │   ├── auth/
│   │   ├── learning/
│   │   └── ...
│   ├── pages/
│   ├── services/
│   └── styles/
├── .github/
│   └── workflows/
├── package.json
└── README.md
```

---

## 13. Ownership and Production Handover

The proposed production handover should include:

- Source code and repository access.
- System architecture documentation.
- Database ERD and data dictionary.
- API and integration documentation.
- Role and permission matrix.
- Case-data security and encryption documentation.
- Learning-resource storage documentation.
- Deployment and environment configuration guides.
- Backup, restoration and disaster-recovery procedures.
- Security testing and remediation reports.
- Administrator and user manuals.
- Training materials and handover records.

FAWEZI, BUSE and participating institutions must agree on ownership, operational responsibilities, data governance, hosting, support and maintenance arrangements.

---

## 14. Project Information

**Project:** Gender-Transformative Digital Hub (GTD Hub)

**Programme:** PROGEN-Hub for STEM

**Current demonstrator baseline:** v0.3.5 — Administration, Institutional Insights & M&E

**Post-proposal enhancements:** v0.3.4 Learning Library and v0.3.5 Administration and M&E

**Repository:** https://github.com/gtcharis/gtd-hub-demo

**Demonstrator:** https://gtcharis.github.io/gtd-hub-demo/

**API documentation:** https://gtdhubapi-production.up.railway.app/docs


**Important:** This is a synthetic-data proposal demonstrator, not an operational GBV reporting or case-management service.