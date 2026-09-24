# GymFlow Pro

GymFlow Pro is a SaaS platform for managing gyms, members, staff, subscriptions, payments, attendance, and member progress.

This README describes the **current MVP** and the **planned direction after the first version**.

---

## Current MVP

The first working version includes:

- SaaS Admin
- Gym Admin
- Staff
- Activation Code onboarding
- Authentication and roles
- Member management
- Membership plans
- Subscriptions
- Payments
- Attendance
- Check-in / Check-out
- Body measurements
- Gym dashboard
- Staff management

### Current Stack

- **Frontend:** React + Vite
- **Backend:** FastAPI
- **Database:** PostgreSQL through Supabase
- **Storage:** Supabase Storage
- **Hosting:** Render

### Current Architecture

```text
React / Vite
     |
     v
FastAPI
     |
     v
PostgreSQL / Supabase
     |
     v
Supabase Storage
```

---

# Future Development Plan

The goal is to grow GymFlow Pro into a scalable multi-gym SaaS platform without rebuilding the whole system later.

## 1. Multi-Tenancy

Each gym should be treated as an independent tenant.

```text
Gym A
 ├── Members
 ├── Staff
 ├── Subscriptions
 ├── Payments
 └── Attendance

Gym B
 ├── Members
 ├── Staff
 ├── Subscriptions
 ├── Payments
 └── Attendance
```

Gym data must always be isolated.

Important records should be connected to the correct `gym_id`, and the backend should determine the gym from the authenticated user rather than trusting a gym ID sent by the frontend.

---

## 2. Security

Security should be strengthened before adding many advanced features.

Planned improvements:

- Strong authentication
- Role-based authorization
- Gym-level data isolation
- Secure password handling
- Token/session security
- API validation
- Rate limiting
- Audit logs
- Secure environment variables

---

## 3. Database and Indexing

As the number of gyms and members grows, database queries must stay fast.

Indexes should be added based on real query patterns.

Examples:

```text
gym_id
gym_id + status
gym_id + created_at
gym_id + member_id
```

We should not add indexes to every column without a reason.

---

## 4. Redis and Caching

Redis is planned for a later stage.

Possible uses:

- Dashboard caching
- Temporary data
- Rate limiting
- OTP / temporary activation data
- Sessions where appropriate
- Background job queues
- Temporary AI results

PostgreSQL remains the main source of truth.

Redis should not replace the main database.

---

## 5. Background Jobs

Long-running tasks should eventually run outside normal API requests.

Examples:

- Sending notifications
- Generating reports
- Subscription reminders
- Large data processing
- AI processing

Future flow:

```text
FastAPI
   |
   v
Job Queue
   |
   v
Background Worker
   |
   +--> Notifications
   +--> Reports
   +--> AI Tasks
```

This keeps the main API responsive.

---

## 6. Search

A separate search engine is not required immediately.

Planned progression:

```text
Stage 1
PostgreSQL indexes

Stage 2
PostgreSQL full-text search

Stage 3
Dedicated search engine if needed
```

Possible future technologies:

- OpenSearch
- Elasticsearch

The choice should depend on real data size and search requirements.

---

## 7. QR Attendance

A future version may support QR-based gym entry.

Possible flow:

```text
Member
   |
   v
QR Code
   |
   v
GymFlow Backend
   |
   +--> Validate QR
   +--> Validate Gym
   +--> Validate Membership
   +--> Create Attendance
```

QR codes should not expose sensitive member information.

---

## 8. Mobile App

A future mobile app can allow members to:

- View membership
- View subscription status
- Renew membership
- Make payments
- View attendance
- View measurements
- Follow workouts
- Receive notifications
- Use QR for gym entry
- Use AI assistance

The mobile app should use the same FastAPI backend as the web application.

```text
React Web App
       |
       +------> FastAPI <------+
                              |
Mobile App -------------------+
                              |
                              v
                       PostgreSQL
```

---

## 9. Payments

Payments should eventually become a complete workflow.

Planned structure:

```text
Subscription
      |
      v
Invoice
      |
      v
Payment
      |
      +--> Payment Method
      +--> Status
      +--> Transaction ID
```

Future versions can support online payments and different payment methods depending on the target market.

---

## 10. AI Features

AI will be added gradually.

Possible features:

- Personalized workout assistance
- Exercise recommendations
- Nutrition assistance
- Member progress analysis
- Smart recommendations
- Gym insights
- AI assistant for members

For heavy AI tasks, the future architecture can use background workers:

```text
Mobile / Web
     |
     v
FastAPI
     |
     v
Job Queue
     |
     v
AI Worker
     |
     v
AI Provider
```

The goal is to keep AI workloads from slowing down the main API.

---

## 11. Storage

Files such as:

- Member images
- Reports
- PDFs
- Gym documents
- AI-generated files

should be stored in object storage instead of the application server.

Current direction:

```text
PostgreSQL
    |
    +--> File metadata

Supabase Storage
    |
    +--> Actual files
```

---

## 12. Monitoring and Reliability

As GymFlow grows, monitoring should be added.

Planned capabilities:

- Application logs
- Error tracking
- Health checks
- API response-time monitoring
- Database monitoring
- Request metrics
- Background-job monitoring

The goal is to quickly know when something fails and where it happened.

---

# Infrastructure Direction

## Render

Render is suitable for the current MVP and early growth.

We do not need to move to AWS or Azure just because they can support larger infrastructure.

The first approach is:

```text
MVP / Early Growth
        |
        v
Render + Supabase
```

If the system becomes large enough to require more infrastructure control:

```text
Render
   |
   | migrate when justified
   v
AWS / Azure / another cloud
```

The application should remain as cloud-independent as practical.

Docker and environment-based configuration can make a future migration easier.

The decision to migrate should be based on real measurements such as:

- Traffic
- API requests
- Database load
- Number of gyms
- Number of users
- Background jobs
- AI workload
- Cost
- Reliability requirements

---

# Supabase vs Firebase

The current direction is to continue with **PostgreSQL / Supabase**.

GymFlow has a highly relational data model:

```text
Gym
 |
 +--> Members
 |
 +--> Staff
 |
 +--> Plans
 |
 +--> Subscriptions
 |
 +--> Payments
 |
 +--> Attendance
 |
 +--> Measurements
```

Because of this, PostgreSQL is a good fit.

There is currently no need to migrate to Firebase.

This decision can be revisited if product requirements change significantly.

---

# Development Roadmap

## Phase 1 — Stabilize the MVP

Focus on correctness and security.

- Fix current bugs
- Improve authentication
- Improve authorization
- Verify gym data isolation
- Improve database constraints
- Add important indexes
- Improve error handling
- Improve loading states
- Improve API validation

## Phase 2 — Business Features

- Better payments
- Invoices
- Expenses
- Reports
- Subscription reminders
- Notifications
- Trainer management
- More staff roles

## Phase 3 — Member Experience

- Mobile app
- QR attendance
- Online renewal
- Online payments
- Member notifications
- Workout tracking
- Progress tracking

## Phase 4 — Smart Features

- AI workout assistant
- Nutrition assistance
- Personalized recommendations
- Member progress analysis
- Gym analytics
- Retention insights

## Phase 5 — Scaling

Add infrastructure only when real usage requires it:

- Redis
- Background workers
- Better monitoring
- Autoscaling
- Database optimization
- Read replicas
- Dedicated search
- Separate AI services

---

# Main Principle

> **Build the application correctly first, then scale the infrastructure according to real usage.**

We do not need to build infrastructure for millions of gyms today.

The goal is to make the MVP ready to grow:

```text
1 Gym
  ↓
10 Gyms
  ↓
100 Gyms
  ↓
1,000+ Gyms
```

without requiring a complete rewrite.

---

## Current Status

**Version:** MVP v1  
**Status:** First working production deployment

### Current

```text
Frontend  → React + Vite
Backend   → FastAPI
Database  → PostgreSQL / Supabase
Storage   → Supabase Storage
Hosting   → Render
```

### Planned

```text
Redis
Background Workers
QR
Payments
Mobile App
Search
AI
Analytics
Autoscaling
```

These are planned improvements, not requirements for the current MVP.
