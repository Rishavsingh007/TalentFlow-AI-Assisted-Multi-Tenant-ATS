# TalentFlow — AI-Assisted Multi-Tenant ATS

Multi-tenant applicant tracking system built as a Django REST API. Companies register, authenticate with JWT, publish jobs, manage recruiter pipelines, and receive public applications with resume uploads — all behind row-level tenant isolation.

## Tech stack

| Layer | Technology |
| --- | --- |
| Backend | Python 3.12, Django 5, Django REST Framework |
| Auth | djangorestframework-simplejwt (email login) |
| API docs | drf-spectacular |
| Database | PostgreSQL 16 |
| Cache / broker | Redis 7, django-redis |
| Async | Celery |
| Email (dev) | MailHog |
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
| `GET` / `POST` | `/api/v1/companies/{slug}/jobs/` | JWT | List jobs (members) or create draft (recruiter/admin) |
| `GET` / `PATCH` | `/api/v1/companies/{slug}/jobs/{id}/` | JWT | Retrieve job (members) or update (recruiter/admin) |
| `POST` | `/api/v1/companies/{slug}/jobs/{id}/publish/` | JWT | Publish draft job (recruiter/admin) |
| `GET` | `/api/v1/companies/{slug}/applications/` | JWT | List applications; filters: `job`, `current_stage`, `status` |
| `GET` | `/api/v1/companies/{slug}/applications/{id}/` | JWT | Application detail with candidate and pipeline stages |
| `PATCH` | `/api/v1/companies/{slug}/applications/{id}/stage/` | JWT | Move application stage (recruiter/admin) |
| `GET` | `/api/v1/companies/{slug}/applications/{id}/score/` | JWT | Read AI score and summary (members) |
| `POST` | `/api/v1/companies/{slug}/applications/{id}/score/` | JWT | Re-score application (recruiter/admin) |
| `GET` | `/api/v1/companies/{slug}/audit-logs/` | JWT | Paginated audit trail; filters: `action`, `object_type` |
| `GET` | `/api/v1/jobs/` | No | Public list of open jobs |
| `GET` | `/api/v1/jobs/{id}/` | No | Public detail for an open job |
| `POST` | `/api/v1/jobs/{id}/apply/` | No | Submit application (multipart: name, email, phone, resume) |
| `GET` | `/health/` | No | Health check |
| `GET` | `/api/docs/` | No | Swagger UI |

### Async & AI (Phase 5)

After apply, resume parsing and AI scoring run in **Celery** (web returns 201 immediately). Use `AI_PROVIDER=mock` for offline demo and CI.

| Step | Task | Result |
| --- | --- | --- |
| Apply | `parse_resume` + `send_application_received_email` | Queued on commit |
| Parse | No-op scan → PDF/DOCX text extraction | `Candidate.parsed_resume_text` |
| Score | `ScoringProvider` (mock by default) | `Application.ai_score`, `ai_summary`, `ai_scored_at` |
| Audit | `application.scored` or `application.scoring_failed` | Append-only audit row |

**Score API:** `GET|POST /api/v1/companies/{slug}/applications/{id}/score/` — POST requires recruiter/admin (403 for hiring_manager).

**Local email:** MailHog UI at [http://localhost:8025/](http://localhost:8025/) when using Docker Compose.

### Audit (Phase 4)

Append-only audit trail for business actions — not raw ORM saves. `log_action` is called from the service layer inside existing transactions.

| Action | Trigger | Actor |
| --- | --- | --- |
| `job.published` | `POST .../jobs/{id}/publish/` | JWT user |
| `application.submitted` | `POST /jobs/{id}/apply/` | `null` (public apply) |
| `application.stage_changed` | `PATCH .../applications/{id}/stage/` | JWT user |
| `application.scored` | Celery `score_application` | `null` or JWT user (re-score) |
| `application.scoring_failed` | Celery scoring failure | `null` |

**Audit API:** `GET /api/v1/companies/{slug}/audit-logs/` — company members only (404 for non-members). Optional filters: `?action=`, `?object_type=`. Newest first.

### RBAC (Phase 3)

| Role | List applications | Move stage | Create/edit/publish jobs |
| --- | --- | --- | --- |
| `admin` | yes | yes | yes |
| `recruiter` | yes | yes | yes |
| `hiring_manager` | yes | no (403) | no (403) |
| non-member | 404 | 404 | 404 |

Authorization uses `CompanyMember.role`, not `User.role`.

## Demo seed data

After Docker is up:

```bash
docker compose exec web python scripts/seed_demo.py
```

| Tenant | Slug | User | Password | Role |
| --- | --- | --- | --- | --- |
| Acme Corp | `acme-corp` | `admin@acme.com` | `demo-password-123` | admin |
| Acme Corp | `acme-corp` | `recruiter@acme.com` | `demo-password-123` | recruiter |
| Globex Inc | `globex-inc` | `recruiter@globex.com` | `demo-password-123` | recruiter |

Globex exists to demo cross-tenant isolation (Acme users get 404 on Globex resources).

## Project structure

```
config/                 # Django settings, urls, wsgi
apps/
  accounts/             # User model (email login), register, JWT views
  companies/            # Company, CompanyMember, access helpers
  jobs/                 # Job model, publish service, public + company APIs
  candidates/           # Candidate profiles and resume storage
  applications/         # Application model, apply flow, move_stage pipeline
  ai_scoring/           # Celery parse/score tasks, ScoringProvider
  notifications/        # Application received email task
  audit/                # Append-only AuditLog and log_action service
  core/                 # Health check, permissions, upload validation, scan stub
scripts/
  seed_demo.py          # Acme + Globex demo tenants
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
docker compose exec web python scripts/seed_demo.py
```

- Swagger: [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
- Health: [http://localhost:8000/health/](http://localhost:8000/health/)
- MailHog: [http://localhost:8025/](http://localhost:8025/)
- Celery worker starts automatically (`celery_worker` service)

Uploaded resumes are persisted in the `media_data` Docker volume.

## Quick start (local venv)

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows
pip install -r requirements-dev.txt

cp .env.example .env
docker compose up -d db redis mailhog

python manage.py migrate
python scripts/seed_demo.py
# Terminal 2: celery -A config worker -l info
python manage.py runserver
```

## API examples

On **Windows PowerShell**, prefer `Invoke-RestMethod` (bash `curl` quoting often breaks JSON).

**Login (after seed):**

```powershell
$tokens = Invoke-RestMethod -Method POST -Uri "http://localhost:8000/api/v1/auth/login/" `
  -ContentType "application/json" `
  -Body (@{
    email    = "recruiter@acme.com"
    password = "demo-password-123"
  } | ConvertTo-Json)

$headers = @{ Authorization = "Bearer $($tokens.access)" }
```

**List pipeline applications:**

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/companies/acme-corp/applications/" -Headers $headers
```

**Filter by stage:**

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/companies/acme-corp/applications/?current_stage=Screening" -Headers $headers
```

**Move application stage:**

```powershell
Invoke-RestMethod -Method PATCH `
  -Uri "http://localhost:8000/api/v1/companies/acme-corp/applications/1/stage/" `
  -Headers $headers `
  -ContentType "application/json" `
  -Body (@{ current_stage = "Interview" } | ConvertTo-Json)
```

**View audit trail (after moving stages or publishing jobs):**

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/companies/acme-corp/audit-logs/" -Headers $headers
```

**Filter audit logs by action:**

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/companies/acme-corp/audit-logs/?action=application.stage_changed" -Headers $headers
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

**Apply with resume (use curl on older PowerShell — no `-Form` support):**

```powershell
curl.exe -X POST "http://localhost:8000/api/v1/jobs/1/apply/" `
  -F "full_name=Jane Doe" `
  -F "email=jane@example.com" `
  -F "phone=555-1234" `
  -F "resume=@resume.pdf;type=application/pdf"
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
| `REDIS_URL` | Redis cache and Celery broker |
| `AI_PROVIDER` | `mock` (default), `openai`, or `anthropic` |
| `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` | Live AI providers (optional) |
| `EMAIL_HOST` / `EMAIL_PORT` | MailHog in Docker (`mailhog:1025`) |
| `CORS_ALLOWED_ORIGINS` | Allowed browser origins |
| `API_KEY_PEPPER` | Secret for API key hashing |

## License

Personal portfolio project.
