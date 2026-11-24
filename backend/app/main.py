import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.api.auth_routes import router as auth_router

app = FastAPI(
    title="GTD Hub Demonstrator API",
    version="0.2.4",
    description="Authenticated proposal demonstrator API. Fictional demonstration data only.",
)
origins = [x.strip() for x in os.getenv(
    "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,https://gtcharis.github.io"
).split(",") if x.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
app.include_router(router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
