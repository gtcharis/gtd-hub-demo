from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

app = FastAPI(
    title="GTD Hub Demonstrator API",
    version="0.2.0",
    description="Proposal-stage API scaffold. Fictional demonstration data only."
)

origins = [x.strip() for x in __import__("os").getenv(
    "CORS_ORIGINS", "http://localhost:5173"
).split(",") if x.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["Content-Type"],
)

app.include_router(router, prefix="/api/v1")
