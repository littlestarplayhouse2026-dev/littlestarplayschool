# Phase 3 implementation checklist

## P0 — Correctness and production safety
- [x] Audit login/session, role checks, CSRF, password hashing, logout, and expiry; existing auth tests cover login/session/logout. Live PostgreSQL auth remains a deployment smoke check.
- [x] Audit public notice/document/file access against publication windows and privacy; existing services/routes enforce these gates and draft privacy has a test.
- [x] Upload failures roll back metadata and remove written binaries; referenced files are protected from deletion. Added an isolated upload validation/access/delete test and fixed storage path resolution.
- [x] Production startup requires PostgreSQL, private session secret, HTTPS origins, absolute upload path, and explicit persistent-volume declaration.
- [x] `.env` files are ignored; public response schemas omit private inquiry/session fields. The repository's attached `.git` metadata is unavailable to `git status`, so source-control tracking should be confirmed in the real Git checkout.

## P1 — Complete administrator and public workflows
- [x] Dashboard reads real database counts and recent items; UI/API have been audited, but metric parity for scheduled/expired edge cases is not covered by dedicated tests.
- [x] Inquiry list/detail/status/delete, search, pagination and submission validation/rate limiting exist; only submission and access guards are directly covered in the current suite.
- [x] Notice management and publication routes/UI exist, including draft privacy and server-side rich text sanitization. No dedicated scheduled/expiry regression tests yet.
- [x] Document management and public download gates exist; basic CRUD is tested. Replace/schedule/expiry/download denial need dedicated regression tests.
- [x] Upload search/filter, selection/references, validation, authorization, and deletion workflow exists; upload test covers invalid extension, private download, authorized download, and delete. Browser progress and gallery remain manual UI checks.
- [ ] Browser-level checks for loading/error/retry states, nested-route refresh, responsive layout, and English/Nepali switching.

## P2 — Deployment, recovery, verification, and handover
- [ ] Review all model constraints, indexes, migrations, and timestamp handling. No production database schema changes were made; the live migration state was not queried.
- [ ] Test coverage is improved for health headers and upload access/validation, but scheduled/expiry, role-specific, transaction failure, inquiry status, and downloads for published documents still need tests.
- [x] Backend suite (including isolated API workflow) and frontend production build passed. Full live browser-to-Supabase E2E was not run to avoid modifying production data; no local browser automation is configured.
- [x] Added production config examples, pinned runtime requirements, startup/migration and static hosting instructions, persistent storage guidance, recovery commands, security controls, and known limitations.
- [x] Removed the confirmed zero-byte stale `backend/littlestar.db`; preserved existing Supabase records and uploaded files.
