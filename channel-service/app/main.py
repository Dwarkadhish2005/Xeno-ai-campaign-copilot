from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers.messages import router as messages_router

app = FastAPI(
    title="Xeno AI Campaign Copilot - Channel Service",
    description="Message delivery simulation service",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(messages_router)
