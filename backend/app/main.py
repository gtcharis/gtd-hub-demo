import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse
from app.api.routes import router
from app.api.auth_routes import router as auth_router
from app.api.mentorship_routes import router as mentorship_router
from app.api.community_routes import router as community_router
from app.api.case_routes import router as case_router
from app.api.learning_routes import router as learning_router
from app.api.admin_routes import router as admin_router
from app.api.dashboard_routes import router as dashboard_router

app = FastAPI(
    title="GTD Hub Demonstrator API",
    version="0.3.7",
    description="Authenticated proposal demonstrator API. Fictional demonstration data only. v0.3.7 member engagement indicators and v0.3.6 role-aware database-backed overview dashboards; v0.3.5 administration, institutional insights and M&E; v0.3.4 learning library.",
)
origins = [x.strip() for x in os.getenv(
    "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,https://gtcharis.github.io"
).split(",") if x.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH","DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
app.include_router(router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(mentorship_router, prefix="/api/v1")
app.include_router(community_router, prefix="/api/v1")
app.include_router(case_router, prefix="/api/v1")
app.include_router(learning_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")

@app.middleware("http")
async def enforce_https(request: Request, call_next):
    if os.getenv("REQUIRE_HTTPS", "false").lower() == "true":
        forwarded = request.headers.get("x-forwarded-proto", "").split(",")[0].strip().lower()
        if request.url.scheme != "https" and forwarded != "https":
            return JSONResponse(status_code=400, content={"detail": "HTTPS is required"})
    return await call_next(request)
