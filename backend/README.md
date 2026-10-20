# FastAPI backend

The complete local setup, configuration, migration, deployment, backup, and restore guide is in the [repository README](../README.md).

Quick commands from this directory:

```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
python -m app.cli create-admin
PYTHONPATH=. uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Run tests with `PYTHONPATH=. pytest -v`. For deployment, install `requirements-prod.txt` and configure PostgreSQL, HTTPS trusted origins, a private session secret, and a persistent upload volume as described in the root README. Never commit `.env` files.
