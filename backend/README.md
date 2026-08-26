# Gym SaaS Backend

Backend-only multi-tenant Gym SaaS API built with FastAPI, SQLAlchemy and PostgreSQL/Supabase.

## Architecture

`FastAPI -> Dependencies/Auth -> Services -> Repositories -> SQLAlchemy -> PostgreSQL`

The frontend has been removed. The backend is consumed through REST APIs and OpenAPI at `/docs`.

## Authentication

- Username + password only.
- No public signup.
- No role selection.
- Application identity is the `users` table.
- Roles: `saas_admin`, `gym_admin`, `staff`.
- Passwords are bcrypt hashes.
- Gym Admin and Staff accounts start as `pending_password` and use one-time setup tokens.
- JWT carries user id, role, and gym id for gym users.

## Tenant isolation

Gym-owned resources derive `gym_id` from the authenticated user. Client-provided `gym_id` is never trusted.

## API

- `/api/v1/auth/*`
- `/api/v1/saas/*`
- `/api/v1/gym/*`
- `/api/v1/staff/*`
- `/api/v1/plans/*`
- `/api/v1/members/*`
- `/api/v1/subscriptions/*`
- `/api/v1/payments/*`
- `/api/v1/attendance/*`
- `/api/v1/members/{member_id}/measurements`

## Run

```bash
cd gym-saas-backend
python -m venv .venv
# activate the environment
pip install -r ../requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

The database schema is assumed to already exist. This project does not create or migrate the schema automatically.
