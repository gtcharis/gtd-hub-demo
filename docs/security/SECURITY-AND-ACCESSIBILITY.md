# Demonstrator security and accessibility notes

## Security boundary
This proposal demonstrator contains fictional data only. It has no authentication, no real report submission, no private case storage and no live notification/referral integration. UI role switching is a demonstration convenience and is not an access-control mechanism.

## OWASP alignment
The demonstrator should be reviewed against the OWASP Top 10 as a design and testing exercise. Current implementation controls include:
- API calls are HTTPS-ready and use a configurable API origin.
- API CORS is allow-list configured.
- Demo API is read-only.
- No secrets or personal data are embedded in client-side configuration.
- No sensitive API responses are cached by the service worker (`NetworkOnly` for `/api/`).
- No live report endpoint exists.

This does not constitute an OWASP assessment or security certification.

## WCAG 2.1 AA target
- Semantic headings, navigation and buttons.
- Accessible names on icon-only controls.
- Visible keyboard focus.
- Native inputs and checkbox semantics.
- Responsive reflow and touch-friendly controls.
- Reduced-motion preference support.
- Status feedback uses `role=status`.

A full WCAG 2.1 AA claim requires manual keyboard and screen-reader review, automated scans, contrast checks and testing at zoom/reflow settings. Do not describe the demonstrator as certified.

## Production requirements not implemented here
Authentication and session security, server-side RBAC, organisation tenant isolation, encryption, protected case store, consent and withdrawal records, tamper-evident audit logs, retention/deletion, incident response, threat modelling, OWASP ASVS verification and independent security testing.
