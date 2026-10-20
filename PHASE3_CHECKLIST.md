# Phase 3 implementation checklist

## P0 — Correctness and production safety
- [x] Audit login/session, role checks, CSRF, password hashing, logout, and expiry; existing auth tests cover login/session/logout. Live PostgreSQL auth remains a deployment smoke check.
- [x] Audit public notice/document/file access against publication windows and privacy; existing services/routes enforce these gates and draft privacy has a test.
- [x] Upload failures roll back metadata and remove written binaries; referenced files are protected from deletion. Added an isolated upload validation/access/delete test and fixed storage path resolution.
- [x] Production startup requires a PostgreSQL URL with TLS, private session secret, exact origin-only HTTPS origins, absolute upload path, and explicit persistent-volume declaration; port, size, session-age, and rate-limit settings must be valid positive values.
- [x] `.env` files are ignored; public response schemas omit private inquiry/session fields. The repository's attached `.git` metadata is unavailable to `git status`, so source-control tracking should be confirmed in the real Git checkout.

## P1 — Complete administrator and public workflows
- [x] Dashboard metrics match currently public notice/document visibility and scheduled items are advanced by reads; workflow tests assert publish/unpublish counts.
- [x] Inquiry list/detail/status/delete, search, pagination, validation, rate limiting, and honeypot behavior are exercised with synthetic tests.
- [x] Notice create/draft/publish, draft privacy, scheduled visibility, expiry, sanitization, missing attachment handling, and expiry-order validation are covered across API tests and browser workflow.
- [x] Duplicate-slug races return HTTP 409 with retry guidance; notice and document edits take PostgreSQL row locks. The conflict response has a regression test, and PostgreSQL SQL compilation confirms both edit queries emit `FOR UPDATE`.
- [x] Document create/edit/delete, schedule, expiry, upload/download, unpublish privacy, and dashboard metrics are covered across tests and browser workflow.
- [x] Upload search/filter, actual XHR progress, file selection, extension/signature validation, unauthorized download, editor/admin access, referenced-file protection, and gallery flow are implemented; synthetic Firefox workflow exercised document and gallery uploads.
- [x] Firefox smoke check covered homepage, direct nested routes and refresh, English/Nepali nav toggle, and admin sign-in. The headless browser has a 488 CSS-pixel minimum viewport; this is inside the app's mobile breakpoint and showed no page-level horizontal overflow.
- [x] Firefox checked public notice and document API failure states, the homepage notice retry action, and the gallery retry control against an unavailable local API. Direct `/documents` navigation and refresh retained the route. Headless Firefox reports a 488px minimum CSS viewport, so narrower layouts remain unverified.
- [x] Authenticated Firefox check against a disposable SQLite API confirmed the dashboard and messages show API errors with retry controls; clicking Retry repeats the request and leaves the actionable error visible.
- [ ] Verify layouts below Firefox's 488px CSS viewport minimum on a real or emulated narrow-screen device. All public routes and `/admin` were checked at Firefox's 500px minimum inner width after fixing the notice category scroller; no page-level horizontal overflow remained.

## P2 — Deployment, recovery, verification, and handover
- [x] Reviewed model foreign keys, uniqueness, indexes, UTC timestamps, and migration lineage; offline PostgreSQL SQL generation succeeds through `0004_gallery_items`. A read-only query confirmed live Supabase is at `0004_gallery_items`, and the app's `/api/health` returned HTTP 200 after `SELECT 1`; no migration or data write was run.
- [x] Added regression coverage for auth/session/logout/roles, status and expiry visibility, validation, inquiries, dashboard, file authorization, file-signature cleanup, request size, upload cleanup after injected database commit failure, and integrated publishing workflows.
- [x] Backend suite: `venv/bin/python -m pytest -q` passed, 38 tests in 5.19s, using the in-memory SQLite test fixtures. `venv/bin/python -m pip check` reported no broken requirements. `npm audit --audit-level=low` reported 0 vulnerabilities; `pip-audit -r backend/requirements-prod.txt` reported no known vulnerabilities. Frontend `npm run build` passed. Firefox browser checks and the earlier browser-to-isolated-API workflow passed. No production/Supabase test records were created.
- [x] Added production config examples, pinned runtime requirements, startup/migration and static hosting instructions, persistent storage guidance, recovery commands, security controls, and known limitations.
- [x] Removed the confirmed zero-byte stale `backend/littlestar.db`; preserved existing Supabase records and uploaded files.

## Remaining external verification
- [x] Confirmed deployed Supabase schema is at `0004_gallery_items` with a read-only query. No production migration was run.
- [ ] Mount and verify a durable upload volume, configure production HTTPS origins/cookies, and test recovery of PostgreSQL plus the matching upload backup in an isolated environment.
- [ ] Run the documented browser checks against the deployed custom domain and a physical narrow-screen device; no production deployment or backup restoration was performed during this audit.
