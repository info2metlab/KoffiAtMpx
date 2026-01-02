# KoffiAtMpx

Django project configured for a Siemens IPC target using MySQL.

## Setup
1. Ensure system MySQL client libraries are available (e.g., `libmysqlclient-dev`).
2. Create a virtual environment and install dependencies:
   - `python -m venv .venv`
   - `. .venv/bin/activate`
   - `pip install -r requirements.txt`
3. Copy environment defaults and adjust:
   - `cp .env.example .env`
   - Set `DJANGO_SECRET_KEY`, database credentials, and allowed hosts.
4. Apply migrations and run:
   - `python manage.py migrate`
   - `python manage.py runserver 0.0.0.0:8000`

## Health check
- `GET /health/` returns a JSON status payload.

## Database configuration
- Default engine is MySQL.
- Controlled by env vars: `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_DB`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_CONN_MAX_AGE`.
- For local tooling without MySQL, set `DB_ENGINE=sqlite` (uses `db.sqlite3`).

## Repository
- Intended GitHub target: `https://github.com/info2metlab/KoffiAtMpx` (set your remote and push with credentials).
