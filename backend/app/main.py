from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from .config import settings
from .schemas import HealthResponse
from .routers import upload as upload_router
from .routers import intelligence as intelligence_router
from .routers import campaigns as campaigns_router
from .routers import audience as audience_router
from .routers import analytics as analytics_router

app = FastAPI(
    title="Xeno AI Campaign Copilot - Backend",
    description="AI-Native Customer Engagement Platform",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router.router)
app.include_router(intelligence_router.router)
app.include_router(campaigns_router.router)
app.include_router(audience_router.router)
app.include_router(analytics_router.router)


@app.get("/health")
async def health():
    payload = {"status": "ok", "timestamp": datetime.utcnow().isoformat()}
    return {"success": True, "data": payload, "message": "OK"}
