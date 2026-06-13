# TalentFlow — AI-Assisted Multi-Tenant ATS

Multi-tenant applicant tracking system built as a Django REST API. Companies register, authenticate with JWT, publish jobs, and receive public applications with resume uploads — all behind row-level tenant isolation.

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
| `GET` / `POST` | `/api/v1/companies/{slug}/jobs/` | JWT | List or create draft jobs (members only) |
| `GET` / `PATCH` | `/api/v1/companies/{slug}/jobs/{id}/` | JWT | Retrieve or update a company job |
| `POST` | `/api/v1/companies/{slug}/jobs/{id}/publish/` | JWT | Publish a draft job (`draft → open`) |
| `GET` | `/api/v1/jobs/` | No | Public list of open jobs |
| `GET` | `/api/v1/jobs/{id}/` | No | Public detail for an open job |
| `POST` | `/api/v1/jobs/{id}/apply/` | No | Submit application (multipart: name, email, phone, resume) |
| `GET` | `/health/` | No | Health check |
| `GET` | `/api/docs/` | No | Swagger UI |

Resume parsing and AI scoring are planned for Phase 5 — `parsed_resume_text` and `ai_score` remain empty after apply.

## Project structure

```
config/                 # Django settings, urls, wsgi
apps/
  accounts/             # User model (email login), register, JWT views
  companies/            # Company, CompanyMember, registration service
  jobs/                 # Job model, publish service, public + company APIs
  candidates/           # Candidate profiles and resume storage
  applications/         # Application model and public apply flow
  core/                 # Health check, permissions, upload validation, scan stub
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

Uploaded resumes are persisted in the `media_data` Docker volume.

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

$headers = @{ Authorization = "Bearer $($tokens.access)" }
```

**Company profile:**

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/companies/acme-corp/" -Headers $headers
```

**Create and publish a job:**

```powershell
$job = Invoke-RestMethod -Method POST -Uri "http://localhost:8000/api/v1/companies/acme-corp/jobs/" `
  -Headers $headers `
  -ContentType "application/json" `
  -Body (@{
    title            = "Backend Engineer"
    description      = "Build APIs with Django"
    department       = "Engineering"
    location         = "Remote"
    employment_type  = "full_time"
  } | ConvertTo-Json)

Invoke-RestMethod -Method POST -Uri "http://localhost:8000/api/v1/companies/acme-corp/jobs/$($job.id)/publish/" `
  -Headers $headers
```

**List public jobs:**

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/jobs/"
```

**Apply with resume (PDF or DOCX, max 5 MB):**

```powershell
Invoke-RestMethod -Method POST -Uri "http://localhost:8000/api/v1/jobs/$($job.id)/apply/" `
  -Form @{
    full_name = "Jane Doe"
    email     = "jane@example.com"
    phone     = "555-1234"
    resume    = Get-Item -Path ".\resume.pdf"
  }
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
