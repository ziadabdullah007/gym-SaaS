from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.auth_routes import router as auth_router
from app.api.v1.saas_routes import router as saas_router
from app.api.v1.gym_routes import router as gym_router
from app.api.v1.staff_routes import router as staff_router
from app.api.v1.plan_routes import router as plan_router
from app.api.v1.member_routes import router as member_router
from app.api.v1.subscription_routes import router as subscription_router
from app.api.v1.payment_routes import router as payment_router
from app.api.v1.attendance_routes import router as attendance_router
from app.api.v1.body_measurement_routes import router as measurement_router

app = FastAPI(title="Gym SaaS API", version="2.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in [
    auth_router, saas_router, gym_router, staff_router, plan_router,
    member_router, subscription_router, payment_router, attendance_router,
    measurement_router,
]:
    app.include_router(router)

@app.get("/", tags=["Health"])
def root():
    return {"message": "Gym SaaS API Running", "docs": "/docs", "version": app.version}

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "service": "gym-saas-api", "version": app.version}
