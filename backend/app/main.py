from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes.dashboard import router as dashboard_router
from app.core.config import settings
from app.services.dashboard import DashboardUnavailableError


app = FastAPI(
    title="REST API Integration and Backend Workflow",
    description="Repository Activity Dashboard API with GitHub integration, normalization, caching, and workflow-friendly endpoints.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.exception_handler(DashboardUnavailableError)
async def dashboard_unavailable_handler(
    request: Request, exc: DashboardUnavailableError
) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={
            "error": {
                "code": "dashboard_unavailable",
                "message": str(exc),
                "details": "GitHub data could not be loaded right now. Cached data will be used automatically when available.",
                "path": str(request.url.path),
            }
        },
    )


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "repository-activity-dashboard"}


app.include_router(dashboard_router, prefix="/api/dashboard", tags=["dashboard"])
