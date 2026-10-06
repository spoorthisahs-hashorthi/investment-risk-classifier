"""Main FastAPI application entrypoint."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.config import settings
from app.api.v1.endpoints import router as api_v1_router
from app.models.schemas import APIErrorResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("risk_analysis_backend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION} [{settings.ENVIRONMENT}]")
    yield
    logger.info("Shutting down risk analysis backend service.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "Rules-based educational screening API for submitted investment promotion text and URL structure. "
        "Submitted websites are not contacted; results include evidence and uncertainty."
    ),
    lifespan=lifespan,
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Global validation exception handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_messages = []
    for err in exc.errors():
        field = " -> ".join(str(loc) for loc in err.get("loc", []))
        msg = err.get("msg", "Invalid value")
        error_messages.append(f"{field}: {msg}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=APIErrorResponse(
            error="Validation Error",
            details=error_messages,
            message="Input validation failed. Please review the submitted parameters.",
        ).model_dump(),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail if isinstance(exc.detail, str) else "The request could not be completed."
    return JSONResponse(
        status_code=exc.status_code,
        headers=exc.headers,
        content=APIErrorResponse(
            error="Validation Error" if exc.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY else "Request Error",
            message=detail,
            details=[],
        ).model_dump(),
    )


# Global unhandled exception handler to avoid leaking internals
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception on {request.method} {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=APIErrorResponse(
            error="Internal Server Error",
            message="An error occurred during analysis. Please try again or simplify the input.",
            details=[],
        ).model_dump(),
    )


# Mount API v1 router
app.include_router(api_v1_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["System"])
async def health_check():
    """Healthcheck endpoint reporting service status."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "live_url_fetch_enabled": False,
    }
