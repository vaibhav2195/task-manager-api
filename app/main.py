from datetime import datetime, timezone
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.dependencies import get_repository
from app.api.routes import router as tasks_router
from app.config import settings
from app.exceptions import (
    DuplicateTaskError,
    RepositoryError,
    TaskNotFoundError,
    TaskValidationError,
)
from app.metrics import get_metrics_response, prometheus_middleware

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Task Manager REST API built with OOP, Pytest, Docker, and CI/CD.",
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(prometheus_middleware)


# Global Exception Handlers
@app.exception_handler(TaskNotFoundError)
async def task_not_found_handler(request: Request, exc: TaskNotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": "Not Found", "message": exc.message},
    )


@app.exception_handler(TaskValidationError)
async def task_validation_handler(request: Request, exc: TaskValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Bad Request", "message": exc.message},
    )


@app.exception_handler(DuplicateTaskError)
async def duplicate_task_handler(request: Request, exc: DuplicateTaskError):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"error": "Conflict", "message": exc.message},
    )


@app.exception_handler(RepositoryError)
async def repository_error_handler(request: Request, exc: RepositoryError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Database Error", "message": exc.message},
    )


# System Endpoints
@app.get("/health", tags=["System"])
def health_check():
    """Health check endpoint validating application and repository status."""
    db_status = "healthy"
    try:
        repo = get_repository()
        repo.count()
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "repository_type": settings.REPOSITORY_TYPE,
        "database_status": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/metrics", tags=["System"])
def metrics():
    """Prometheus metrics endpoint."""
    return get_metrics_response()


# Include Routers
app.include_router(tasks_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
