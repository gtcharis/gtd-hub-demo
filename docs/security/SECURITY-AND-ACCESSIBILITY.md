# Demonstrator security and accessibility notes — v0.2.4

## Security controls implemented
This proposal demonstrator contains fictional data only. It is not a live GBV reporting channel.

- Argon2 password hashing.
- Random opaque bearer session tokens; only SHA-256 token hashes are persisted.
- Eight-hour session expiry and server-side logout revocation.
- Active-user and active-institution checks.
- Backend authentication dependencies and role dependency helper.
- Example administrator-only endpoint used to verify 403/200 access decisions.
- Authenticated access to demonstration overview and mentor endpoints.
- CORS allow-list configuration.
- API responses are not cached by the service worker (`NetworkOnly` for `/api/`).

The frontend persists the bearer token in browser local storage to support the separate GitHub Pages and API origins. This is a demonstrator compromise, not the recommended production session architecture. Production should use a reviewed secure session design, preferably HttpOnly secure cookies or an approved identity provider, with appropriate CSRF protections where relevant.

## Known omissions
No login rate limiting, password reset, MFA, email verification, account lifecycle UI, administrative user-management API, full module permission matrix, comprehensive audit trail, production tenant isolation or production case-data separation. Do not enter real personal or GBV disclosure data.

## OWASP alignment
This does not constitute an OWASP assessment or security certification. A production implementation requires threat modelling, OWASP ASVS verification, dependency review, secure configuration, audit controls, incident response and independent security testing.

## WCAG 2.1 AA target
- Semantic headings, navigation and buttons.
- Accessible names on icon-only controls.
- Visible keyboard focus.
- Native inputs and checkbox semantics.
- Responsive reflow and touch-friendly controls.
- A full WCAG 2.1 AA claim requires manual keyboard and screen-reader review, automated scans, contrast checks and zoom/reflow testing.
