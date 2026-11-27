# GTD Hub v0.3.7 — Member Engagement Indicators

## Scope

This patch extends the existing role-aware dashboard implementation. It preserves all six roles, each role's existing Overview page, role navigation and default landing destinations. The unified `GET /api/v1/dashboard/overview` remains the frontend's primary endpoint.

## Member overview indicators

The Member overview retains its personal mentorship, community and learning-resource cards and adds a separate aggregate participation panel:

- Programme-wide registered accounts associated with participating institutions.
- Programme-wide active mentorship connections.
- Institution-scoped engaged Member accounts and engagement rate.
- Institution-scoped eligible Member denominator.

Published learning resources available to the Member continue to include programme-wide resources and resources assigned to the Member's own institution only. Draft resources and resources assigned to other institutions are excluded.

## Engagement definition

Engagement is measured over a rolling 30-day window. An eligible Member is an active registered Member account at the institution. An eligible Member is counted as engaged once if at least one of the following timestamped activities occurs within the window:

1. Creates a community discussion that is not hidden.
2. Posts a visible reply to a discussion that is not hidden.
3. Submits a mentorship request.
4. Has a mentorship connection created.

The engagement rate is `engaged members / eligible members × 100`. If there are no eligible members, the rate is 0%. Each member is counted once regardless of the number of qualifying activities.

The current demonstrator does not record learning-resource views, so resource access is not counted as engagement. This limitation is made explicit in the UI. The measure is a platform participation indicator, not evidence of gender-transformative outcomes, GBV response quality or programme impact.

## API compatibility and access control

The legacy `GET /api/v1/dashboard/member/overview` route is restored for compatibility. It returns the same Member payload as the unified endpoint. It requires the existing `dashboard:read` permission, returns `401` for unauthenticated requests and `403` for authenticated non-Members.

## Test configuration

The test harness now loads `backend/.env` before reading `TEST_DATABASE_URL`. Explicit environment variables continue to take precedence. Existing PostgreSQL-only and test-database safety checks remain in force.

## Verification

- Python source and test syntax compilation: passed.
- PostgreSQL integration tests: not executed in this build environment; run them against the dedicated local PostgreSQL test database.
- Frontend typecheck/build: the previous v0.3.6 build passed in the user's environment. This patch's frontend build could not be rerun in the packaging environment because npm dependency installation timed out. Rerun `npm ci`, `npm run typecheck` and `npm run build` locally.
- Browser acceptance for all six roles: pending.
