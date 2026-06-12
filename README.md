# TalentFlow — AI-Assisted Multi-Tenant ATS

Multi-tenant applicant tracking system built as a Django REST API. Companies register, authenticate with JWT, and manage their profile behind row-level tenant isolation.

## Tech stack

| Layer | Technology |
| --- | --- |
| Backend | Python 3.12, Django 5, Django REST Framework |
| Auth | djangorestframework-simplejwt (email login) |
| API docs | drf-spectacular |
| Database | PostgreSQL 16 |
| Cache | Redis 7, django-redis |
| Server | Gunicorn (WSGI) |
| Config | django-environ |
| Containers | Docker, docker-compose |
| Testing | pytest, pytest-django, factory_boy |

## API

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/api/v1/auth/register/` | No | Create company, admin user, and JWT |
| `POST` | `/api/v1/auth/login/` | No | Email/password → access + refresh tokens |
| `POST` | `/api/v1/auth/refresh/` | No | Refresh token → new access token |
| `GET` / `PATCH` | `/api/v1/companies/{slug}/` | JWT | Company profile (members only; PATCH requires admin) |
| `GET` | `/health/` | No | Health check |
| `GET` | `/api/docs/` | No | Swagger UI |

## Project structure

```
config/                 # Django settings, urls, wsgi
apps/
  accounts/             # User model (email login), register, JWT views
  companies/            # Company, CompanyMember, registration service
  core/                 # Health check, permissions, exception handler
tests/
docker/entrypoint.sh    # Wait for DB, migrate, start Gunicorn
```

## Prerequisites

- Python 3.12 (`python --version`)
- Docker Desktop

## Quick start (Docker)

```bash
cp .env.example .env
docker compose up --build -d
```

- Swagger: [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
- Health: [http://localhost:8000/health/](http://localhost:8000/health/)

## Quick start (local venv)

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows
pip install -r requirements-dev.txt

cp .env.example .env
docker compose up -d db redis

python manage.py migrate
python manage.py runserver
```

## API examples

On **Windows PowerShell**, prefer `Invoke-RestMethod` (bash `curl` quoting often breaks JSON).

**Register:**

```powershell
Invoke-RestMethod -Method POST -Uri "http://localhost:8000/api/v1/auth/register/" `
  -ContentType "application/json" `
  -Body (@{
    email        = "admin@acme.com"
    password     = "demo-password-123"
    company_name = "Acme Corp"
    industry     = "Technology"
  } | ConvertTo-Json)
```

**Login:**

```powershell
$tokens = Invoke-RestMethod -Method POST -Uri "http://localhost:8000/api/v1/auth/login/" `
  -ContentType "application/json" `
  -Body (@{
    email    = "admin@acme.com"
    password = "demo-password-123"
  } | ConvertTo-Json)

$tokens.access
$tokens.refresh
```

**Company profile:**

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/companies/acme-corp/" `
  -Headers @{ Authorization = "Bearer $($tokens.access)" }
```

**Bash / Git Bash:**

```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@acme.com","password":"demo-password-123","company_name":"Acme Corp","industry":"Technology"}'
```

## Tests

```bash
pip install -r requirements-dev.txt
pytest -v
```

## Environment variables

See [.env.example](./.env.example).

| Variable | Purpose |
| --- | --- |
| `DJANGO_SECRET_KEY` | Django secret |
| `DATABASE_URL` | PostgreSQL connection |
| `REDIS_URL` | Redis cache |
| `CORS_ALLOWED_ORIGINS` | Allowed browser origins |
| `API_KEY_PEPPER` | Secret for API key hashing |

## License

Personal portfolio project.
