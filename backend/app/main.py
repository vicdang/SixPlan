from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routers import auth as auth_router
from app.routers import profile as profile_router


app = FastAPI(
    title="Seat Management System API",
    version="1.0.0",
    docs_url="/docs" if settings.environment == "development" else None,
    redoc_url="/redoc" if settings.environment == "development" else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AppError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400, details: list = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or []


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message, "details": exc.details}},
    )


@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    details = [
        {"field": ".".join(str(x) for x in e["loc"][1:]), "message": e["msg"]}
        for e in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": details,
            }
        },
    )


app.include_router(auth_router.router, prefix="/api/v1")
app.include_router(profile_router.router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}
