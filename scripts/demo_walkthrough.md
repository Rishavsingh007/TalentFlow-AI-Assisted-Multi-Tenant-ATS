# TalentFlow — 5-minute demo walkthrough

## Prerequisites

- Docker Desktop running
- Node.js 18+ (for the demo UI)
- Optional: a PDF resume (repo root `demo-resume.pdf` if present)

## 1. Start the stack and seed

```bash
cp .env.example .env
docker compose up --build -d
docker compose exec web python scripts/seed_demo.py
```

Confirm:

- Health: http://localhost:8000/health/
- Swagger: http://localhost:8000/api/docs/
- MailHog: http://localhost:8025/

## 2. Start the React demo UI

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Open http://localhost:5173/apply

## 3. Public apply (talking point: async Celery)

1. Pick an open job (e.g. Backend Engineer).
2. Submit name, email, and a PDF resume.
3. Note the success message — scoring runs off the request thread.

**Talking point:** Web returns `201` immediately; Celery runs `parse_resume` → mock/live `ScoringProvider`; MailHog shows the received email.

## 4. Recruiter login (talking point: tenant + JWT)

1. Open http://localhost:5173/login  
2. Use:

| Field | Value |
|-------|--------|
| Email | `recruiter@acme.com` |
| Password | `demo-password-123` |
| Company slug | `acme-corp` |

**Talking point:** Signup creates tenant + owner atomically; demo uses seed members. Membership is verified with `GET /companies/{slug}/` (cross-tenant → 404).

## 5. Pipeline + WebSocket (talking point: real-time)

1. Open Pipeline — status badge should show **Connected**.
2. In another tab/window, submit a new application on `/apply`.
3. Watch the card appear (`application.received`), then AI score fill in (`application.scored`).
4. Change a card’s stage via the dropdown (`application.stage_changed`).

**Talking point:** Channels group `company_{id}_dashboard`; auth uses short-lived `ws-ticket`, not a JWT in the query string. Service layer emits audit + WS on stage moves.

## 6. Audit trail (talking point: append-only)

1. Open Audit.
2. Filter by `application.stage_changed` or `application.scored`.
3. Show actor email and metadata (`from_stage` / `to_stage`).

**Talking point:** Business actions go through services → `log_action`; no update/delete API for audit rows.

## 7. Optional clips

| Clip | How |
|------|-----|
| Swagger | http://localhost:8000/api/docs/ — show score or publish endpoints |
| Tenancy | Login as Acme, hit Globex slug in URL → redirect/404; or API `GET /companies/globex-inc/` → 404 |
| RBAC | Hiring manager cannot move stages (403) — use if you seed that role |

## Demo credentials (password for all)

| User | Role | Tenant |
|------|------|--------|
| `recruiter@acme.com` | recruiter | `acme-corp` |
| `admin@acme.com` | admin | `acme-corp` |
| `recruiter@globex.com` | recruiter | `globex-inc` |

## One-liner pitch

> TalentFlow is a multi-tenant ATS where resume scoring runs async through a pluggable AI provider, pipeline moves are audit-logged, and recruiter dashboards update in real time — structured like production SaaS, scoped for a portfolio demo.
