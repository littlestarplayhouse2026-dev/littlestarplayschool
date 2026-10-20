# Little Star Playhouse

React, TypeScript, and Vite frontend with a FastAPI backend, PostgreSQL database, and Alembic migrations. The frontend reads its API origin from `VITE_API_BASE_URL`; the backend stores uploaded file bytes in `UPLOAD_DIR` and file metadata in PostgreSQL.

## Local development

Prerequisites: Node.js 20.19+ (or 22.12+) and Python 3.12+. The project uses pnpm (`packageManager` is recorded in `package.json`).

```sh
pnpm install --frozen-lockfile
cp .env.example .env                 # frontend API URL
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt      # includes tests and SQLite test driver
cp .env.example .env
# Set DATABASE_URL to a PostgreSQL/Supabase connection and SESSION_SECRET to a random secret.
alembic upgrade head
python -m app.cli create-admin       # prompts for username, name, and password
PYTHONPATH=. uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

In a second terminal from the repository root:

```sh
pnpm dev
```

Set the backend `FRONTEND_ORIGINS` to the exact Vite origin (normally `http://localhost:5173`) and root `VITE_API_BASE_URL` to `http://localhost:8000/api`. Never use the sample values as production credentials. The backend's existing `.env` should remain private and must not be copied into source control.

## Configuration

Backend variables are documented in [`backend/.env.example`](backend/.env.example). `DATABASE_URL` accepts PostgreSQL URLs; Supabase PostgreSQL connections are automatically given `sslmode=require` if omitted. Use the provider's direct or session-pooler URL for migrations and confirm its connection limit before selecting a pooler URL for the API.

Production startup validates PostgreSQL, a 32-character private `SESSION_SECRET`, HTTPS-only trusted `FRONTEND_ORIGINS`, an absolute `UPLOAD_DIR`, and `UPLOAD_STORAGE_PERSISTENT=true`. Mount a durable volume at that path and back it up; this application currently stores bytes on a local filesystem, not Supabase Storage. HTTPS is required because production session cookies use `Secure`. Set `VITE_API_BASE_URL` to the deployed API URL ending in `/api`; no source edit is needed to change it.

## Database and administrator

Always run migrations before starting a new release:

```sh
cd backend
source venv/bin/activate
alembic upgrade head
```

Create or update administrator accounts only through the interactive CLI (`python -m app.cli create-admin`). There is no public registration route or production default account. Do not seed the development username/password into production.

## Tests and production build

```sh
cd backend && PYTHONPATH=. pytest -v
cd .. && pnpm build
```

The backend suite uses an isolated in-memory SQLite database and temporary upload directory. Production runtime dependencies are listed in `backend/requirements-prod.txt`; development/test dependencies are in `backend/requirements.txt`.

## Deployment

Deploy frontend and backend independently or behind one HTTPS reverse proxy. Build the frontend with `pnpm install --frozen-lockfile && pnpm build`, then serve `dist/` from a static host with SPA fallback to `index.html`. Set `VITE_API_BASE_URL` at build time to the public API base. Run the API with `uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}` after migrations. Set production variables from a secret manager, including `ENVIRONMENT=production`, PostgreSQL `DATABASE_URL`, random `SESSION_SECRET`, exact HTTPS `FRONTEND_ORIGINS`, an absolute mounted `UPLOAD_DIR`, and `UPLOAD_STORAGE_PERSISTENT=true`. Production cookies use `SameSite=None; Secure` to support separately hosted frontends; browsers may block third-party cookies, so use a same-site custom domain or a shared reverse-proxy origin for reliable sessions. Do not expose the upload directory directly from the web server; the API performs access checks for downloads. `/api/health` checks database connectivity and returns 503 when the database is unavailable. API docs are disabled outside development.

The app enforces a declared HTTP request-body cap (`MAX_REQUEST_MB`, default 50 MB) and per-file size/type checks. Configure the reverse proxy's body limit as well; chunked requests may not carry `Content-Length`. Tune proxy, app and provider upload limits together.

## Backup and recovery

Back up PostgreSQL and the complete `UPLOAD_DIR` as a coordinated recovery set. PostgreSQL may be exported with `pg_dump --format=custom --file=playhouse.dump "$DATABASE_URL"`; restore into a new, empty recovery database with `pg_restore --clean --if-exists --no-owner --dbname "$RESTORE_DATABASE_URL" playhouse.dump` (review provider-specific permissions before using `--clean`). Restore the corresponding upload-volume snapshot to the configured `UPLOAD_DIR`, then run/check `alembic upgrade head` and `/api/health` against the recovery environment. Keep encrypted copies of required deployment configuration in the secret manager; do not include `.env` in backups stored with application artifacts. Retain backups according to school privacy and retention policy and periodically test restore into an isolated environment. No backup or restore has been verified as part of this code change.

## Security and known limits

Sessions are server-side, use hashed random tokens, HttpOnly cookies, expiry and CSRF validation. Production enables Secure cookies, trusted-origin CORS, basic security headers, disables API docs, and rejects insecure production configuration. Login and public enquiry endpoints are rate-limited. Rich text and files are validated server-side.

The app does not yet use object storage, a background scheduler, email notifications, or automated backup orchestration. Scheduled content becomes visible when a public query evaluates its schedule, so no operator interaction is needed, but there is no background transition job. The request-size middleware checks declared `Content-Length`; retain an independent reverse-proxy limit. Review dependency updates and deployment infrastructure regularly. These controls are practical safeguards, not a claim of complete security certification.
