# GymFlow Pro — Connected Full Stack

This package contains the existing Gym SaaS FastAPI backend plus a new functional React/Vite frontend connected to the backend API.

## Structure

```text
gym-saas/
├── backend/
│   └── gym-saas-backend/
└── frontend/
    ├── src/
    ├── index.html
    ├── package.json
    ├── vite.config.js
    └── .env.example
```

## Run backend

```bash
cd backend/gym-saas-backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r ../../requirements.txt
copy .env.example .env
# Configure DATABASE_URL and JWT_SECRET_KEY in .env
uvicorn app.main:app --reload --port 8000
```

API:
- http://localhost:8000
- http://localhost:8000/docs
- http://localhost:8000/health

## Run frontend

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

Set `VITE_API_URL=http://localhost:8000` in `.env` if the backend runs elsewhere.

## Authentication

The UI uses the backend's username/password JWT authentication.

There is no public signup.

When a SaaS Admin provisions a Gym Admin, or a Gym Admin provisions Staff, the API generates a one-time 6-digit activation code. The administrator gives the new user the username and activation code.

Inside the same frontend, the user chooses **First time here? Activate your account**, enters the username and activation code, then creates and confirms a password. The activation code expires after 24 hours and can only be used once.

The frontend calls:

`POST /api/v1/auth/verify-activation`

and then:

`POST /api/v1/auth/setup-password`

## Connected screens / actions

### SaaS Admin
- Dashboard → `/api/v1/saas/dashboard`
- Gyms → list/create/update/disable
- SaaS Plans → list/create/update
- Gym Subscriptions → list/create/update
- Settings → backend connectivity

### Gym Admin
- Dashboard → `/api/v1/gym/dashboard`
- Staff → list/create/update/disable
- Members → list/create/update/delete
- Plans → list/create/update/delete
- Subscriptions → list/create/update
- Payments → list/create
- Attendance → list/check-in/check-out
- Measurements → list/create
- Gym Settings → get/update

### Staff
- Dashboard → `/api/v1/staff/dashboard`
- Members → list/create/update
- Subscriptions → list/create
- Payments → list/create
- Attendance → list/check-in/check-out
- Measurements → list/create

### Member profile
The profile screen connects member data with:
- subscriptions
- payments
- attendance
- measurements

Actions include:
- renew/create subscription
- record payment
- check in
- record measurement
- view subscription history
- export member contract/profile data

## Backend compatibility

The frontend does not send `gym_id` for gym-owned resources. Gym context is resolved by the backend JWT/dependencies.

Payment creation uses only:

```json
{
  "subscription_id": "...",
  "amount": 100,
  "payment_method": "cash"
}
```

Attendance check-in uses only:

```json
{
  "member_id": "..."
}
```

## Verification performed

- Backend Python compilation passed.
- FastAPI application imported with a test SQLite URL.
- OpenAPI generation passed.
- All required routers loaded.
- `/health` endpoint added.
- CORS middleware added so the browser frontend can call the API.
- Frontend source includes API calls for every supported business operation.

The local environment did not have a completed frontend dependency install/build available, so a production `npm run build` could not be completed here. Run `npm install && npm run build` in an environment with npm registry access before deployment.
