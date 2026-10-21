# Little Star Playhouse

React, TypeScript, and Vite frontend with a FastAPI backend, PostgreSQL database, and Alembic migrations. The frontend reads its API origin from `VITE_API_BASE_URL`; the backend stores file metadata in PostgreSQL and can store bytes locally or in a private Supabase Storage bucket.

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

Set the backend `FRONTEND_ORIGINS` to the exact Vite origin (normally `http://localhost:3000`). The root `.env.example` configures the frontend to use `/api` and Vite proxies that path to the local backend at `VITE_DEV_API_PROXY_TARGET`. The public contact links are configured with `VITE_PUBLIC_*` variables. Never use sample values as production credentials. The backend's existing `.env` should remain private and must not be copied into source control.

## Configuration

Backend variables are documented in [`backend/.env.example`](backend/.env.example). `DATABASE_URL` accepts PostgreSQL URLs; production connections are given `sslmode=require` if omitted and insecure PostgreSQL SSL modes are rejected. Supabase URLs also get TLS in development, including pooler hostnames. Use the provider's direct or session-pooler URL for migrations and confirm its connection limit before selecting a pooler URL for the API.

Production startup validates a PostgreSQL URL, a 32-character private `SESSION_SECRET`, trusted origin-only HTTPS `FRONTEND_ORIGINS` values (scheme, host, and optional port; no path), valid positive request/upload/session/rate-limit settings, and the selected storage configuration. `STORAGE_BACKEND=supabase` requires the private server-side `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, and `SUPABASE_STORAGE_BUCKET`; the bucket stays private and downloads are proxied through the API after its existing authorization checks. `STORAGE_BACKEND=local` instead requires an absolute `UPLOAD_DIR` on a durable volume and `UPLOAD_STORAGE_PERSISTENT=true`. HTTPS is required because production session cookies use `Secure`. Set `VITE_API_BASE_URL` to the deployed API URL ending in `/api`; no source edit is needed to change it.

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

Run dependency security checks before release and after dependency updates:

```sh
npm audit
cd backend
python -m pip install pip-audit  # audit tool only; not an application dependency
pip-audit -r requirements-prod.txt
```

## Deployment on a Linux VPS (without containers)

This setup serves the built frontend with Nginx and runs FastAPI as a systemd service. Nginx forwards `/api` to the local API, so the browser uses one HTTPS origin for the site and secure admin cookies. Supabase remains the database. Upload bytes live in `/var/lib/littlestar/uploads`; back up this directory with PostgreSQL.

1. Provision a Linux VPS, point your domain's DNS to it, and allow inbound ports 80 and 443. Install Python 3.12+, Node.js 22+, pnpm 10, Nginx, and Certbot with its Nginx integration.
2. Place the project at `/opt/littlestar`. Create the service account and upload directory:

   ```sh
   sudo useradd --system --home-dir /opt/littlestar --shell /usr/sbin/nologin littlestar
   sudo install -d -o littlestar -g littlestar /var/lib/littlestar/uploads
   ```

3. Configure `backend/.env` from `backend/.env.example`: keep your Supabase PostgreSQL `DATABASE_URL`, generate a private secret with `python3 -c 'import secrets; print(secrets.token_urlsafe(48))'`, set `ENVIRONMENT=production`, set `FRONTEND_ORIGINS` to your exact HTTPS origin, set `UPLOAD_DIR=/var/lib/littlestar/uploads`, and `UPLOAD_STORAGE_PERSISTENT=true`. Do not commit either `.env` file.
4. Install backend dependencies and apply migrations:

   ```sh
   cd /opt/littlestar/backend
   python3 -m venv venv
   venv/bin/pip install -r requirements-prod.txt
   venv/bin/alembic upgrade head
   ```

5. Configure the root `.env` from `.env.example`. Use `VITE_API_BASE_URL=/api` and set the public `VITE_PUBLIC_*` values. Build the frontend:

   ```sh
   cd /opt/littlestar
   pnpm install --frozen-lockfile
   pnpm build
   ```

6. After installing dependencies and building `dist/`, make the app read-only to the API account and protect its secret file:

   ```sh
   sudo chown -R root:littlestar /opt/littlestar
   sudo chmod -R g+rX /opt/littlestar
   sudo chmod 640 /opt/littlestar/backend/.env
   ```

   The API service can read the code and its env file through the `littlestar` group; only the persistent upload directory is writable at runtime.

7. Install and start the API service and Nginx site:

   ```sh
   sudo cp deploy/littlestar-api.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable --now littlestar-api
   sudo cp deploy/nginx-littlestar.conf /etc/nginx/sites-available/littlestar
   # Edit server_name to match your domain, then enable the site:
   sudo ln -s /etc/nginx/sites-available/littlestar /etc/nginx/sites-enabled/littlestar
   sudo nginx -t && sudo systemctl reload nginx
   ```

8. Issue/install the TLS certificate for your domain using Certbot's Nginx integration (for example, `sudo certbot --nginx -d YOUR_DOMAIN`). Check `https://YOUR_DOMAIN/api/health`, then create the administrator:

   ```sh
   cd /opt/littlestar/backend
   sudo -u littlestar venv/bin/python -m app.cli create-admin
   ```

For an update, rebuild the frontend, run `venv/bin/alembic upgrade head` for schema changes, then restart with `sudo systemctl restart littlestar-api`. Check logs with `sudo journalctl -u littlestar-api -f` and `sudo tail -f /var/log/nginx/error.log`. Keep `/var/lib/littlestar/uploads` on durable disk and back it up with the database. Do not serve that directory directly; downloads go through API access checks.

For separate frontend/API hosting, set `VITE_API_BASE_URL` to the HTTPS API base ending in `/api` and configure `FRONTEND_ORIGINS` to the exact HTTPS frontend origin. Cross-site browser cookie restrictions can interfere with admin sign-in, so the same-origin Nginx setup above is recommended. Vite embeds `VITE_PUBLIC_*` values in the static assets; these values are public, not secrets. `/api/health` checks database connectivity and returns 503 when the database is unavailable. API docs are disabled outside development.

The app enforces a streaming HTTP request-body cap (`MAX_REQUEST_MB`, default 50 MB), including chunked requests, plus per-file size/type checks. Configure the reverse proxy's body limit as a second layer and tune proxy, app and provider upload limits together.

## Backup and recovery

Back up PostgreSQL and the complete `UPLOAD_DIR` as a coordinated recovery set. PostgreSQL may be exported with `pg_dump --format=custom --file=playhouse.dump "$DATABASE_URL"`; restore into a new, empty recovery database with `pg_restore --clean --if-exists --no-owner --dbname "$RESTORE_DATABASE_URL" playhouse.dump` (review provider-specific permissions before using `--clean`). Restore the corresponding upload-volume snapshot to the configured `UPLOAD_DIR`, then run/check `alembic upgrade head` and `/api/health` against the recovery environment. Keep encrypted copies of required deployment configuration in the secret manager; do not include `.env` in backups stored with application artifacts. Retain backups according to school privacy and retention policy and periodically test restore into an isolated environment. No backup or restore has been verified as part of this code change.

## Security and known limits

Sessions are server-side, use hashed random tokens, HttpOnly cookies, expiry and CSRF validation. Production enables Secure cookies, trusted-origin CORS, basic security headers, disables API docs, and rejects insecure production configuration. Login and public enquiry endpoints are rate-limited. Rich text and files are validated server-side.

The app does not yet use a background scheduler, email notifications, or automated backup orchestration. Scheduled content becomes visible when a public query evaluates its schedule, so no operator interaction is needed, but there is no background transition job. The request-size middleware checks declared `Content-Length`; retain an independent reverse-proxy limit. Review dependency updates and deployment infrastructure regularly. These controls are practical safeguards, not a claim of complete security certification.

## Deploy backend to Render with Supabase Storage

For a stateless Render service, create a **private** Supabase Storage bucket (for example `playhouse-uploads`) and keep its service-role key only in the Render backend environment. Do not add bucket public access policies. The API uses that key server-side and returns file bytes only after its download route authorizes the request. Set Render's root directory to `backend`, build command to `pip install -r requirements-prod.txt`, and start command to `uvicorn app.main:app --host 0.0.0.0 --port $PORT`. At startup, the service applies pending Alembic migrations before initializing the administrator bootstrap. Configure these backend variables in Render: `DATABASE_URL`, `SESSION_SECRET`, `ENVIRONMENT=production`, `FRONTEND_ORIGINS` (comma separated exact HTTPS origins), `STORAGE_BACKEND=supabase`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_STORAGE_BUCKET`, and optionally `MAX_UPLOAD_MB` / `MAX_REQUEST_MB`. Render supplies `PORT`. Never put the service-role key in Vercel or a `VITE_*` variable.

If shell access is unavailable and you need to create/reset the administrator, temporarily set `ADMIN_BOOTSTRAP_USERNAME` and `ADMIN_BOOTSTRAP_PASSWORD` in the Render backend environment (password must be at least 12 characters), then deploy/restart. The service applies those credentials at startup, including resetting an existing admin with that username. As soon as it starts successfully, remove both variables and save; while present, each restart re-applies that password. Keep these values private and never set them on the frontend.

Before serving traffic, run `alembic upgrade head` from the backend root using the same production environment. Configure Vercel's `VITE_API_BASE_URL` to the Render API URL ending in `/api`. For content currently stored on local disk, preserve access to the old files and database, set the new Supabase environment, and run `python -m app.cli migrate-local-files-to-supabase` once. It verifies each file's recorded size and SHA-256, uploads to the private bucket, then updates that row; originals are retained. If an ephemeral host has already discarded the old bytes, this migration cannot restore them. Review/backup the database and source volume before migration. Then verify `/api/health`, admin sign-in, gallery previews, and published/private document access in the deployed environment.
