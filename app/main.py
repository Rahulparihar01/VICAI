import time
import logging

logger = logging.getLogger(__name__)
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.database import SessionLocal
from app.core.errors import ApiError
from app.routers.auth import auth_router, customer_auth_router
from app.routers.admin import admin_router
from app.routers.billing import billing_router
from app.routers.onboarding import onboarding_router
from app.routers.settings import settings_router, public_settings_router
from app.repositories.setting_repo import SettingRepository

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="VicAI Multi-Tenant API",
)

app.add_middleware(
    CORSMiddleware,
    # allow_origins=settings.cors_origin_list,
    allow_origins=["http://localhost:5173","http://localhost:5174","http://localhost:8000","*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAINTENANCE_CACHE_TTL = 60  # seconds
maintenance_cache = {"value": None, "timestamp": 0}

@app.middleware("http")
async def maintenance_mode_middleware(request: Request, call_next):
    # Exclude specific paths from maintenance mode checks
    path = request.url.path
    if path.startswith("/health") or path.startswith("/api/admin") or path.startswith("/api/auth/login"):
        return await call_next(request)
        
    # Check maintenance mode setting
    try:
        current_time = time.time()
        if current_time - maintenance_cache["timestamp"] > MAINTENANCE_CACHE_TTL:
            db = SessionLocal()
            try:
                setting_repo = SettingRepository(db)
                maintenance = setting_repo.get_setting("maintenance_mode")
                maintenance_cache["value"] = maintenance.value if maintenance else None
                maintenance_cache["timestamp"] = current_time
            finally:
                db.close()
        
        maintenance_val = maintenance_cache["value"]
        if maintenance_val and isinstance(maintenance_val, dict) and maintenance_val.get("enabled") is True:
            return JSONResponse(
                status_code=503,
                content={"error": {"code": "MAINTENANCE_MODE", "message": "The platform is currently undergoing maintenance. Please try again later."}}
            )
    except Exception as e:
        # Log DB errors instead of silently passing
        logger.error(f"Error checking maintenance mode: {e}", exc_info=True)
        
    return await call_next(request)

@app.exception_handler(ApiError)
async def api_error_handler(_request: Request, exc: ApiError) -> JSONResponse:
    headers = {"WWW-Authenticate": "Bearer"} if exc.status_code == 401 else None
    return JSONResponse(
        status_code=exc.status_code,
        headers=headers,
        content={"error": {"code": exc.code, "message": exc.message}},
    )

@app.exception_handler(RequestValidationError)
async def validation_error_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
    details = [{"loc": e["loc"], "msg": e["msg"], "type": e["type"]} for e in exc.errors()]
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "The request data is invalid.",
                "details": details
            }
        },
    )

@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "healthy api"}

app.include_router(auth_router)
app.include_router(customer_auth_router)
app.include_router(admin_router)
app.include_router(billing_router)
app.include_router(onboarding_router)
app.include_router(settings_router)
app.include_router(public_settings_router)
