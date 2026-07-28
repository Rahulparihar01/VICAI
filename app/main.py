from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.errors import ApiError
from app.routers.auth import auth_router
from app.routers.internal_admin import internal_admin_router
from app.routers.invitations import invitations_router

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
app.include_router(internal_admin_router)
app.include_router(invitations_router)
