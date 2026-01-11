from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.api.routers.health import router as health_router
from app.api.routers.resumes import router as resumes_router
from app.api.routers.jobs import router as jobs_router
from app.api.routers.matches import router as matches_router
from app.api.routers.notifications import router as notifications_router
from app.workers.scheduler import start_scheduler

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Job Matching API", version="0.1.0")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(resumes_router, prefix="/api/v1", tags=["resumes"])
app.include_router(jobs_router, prefix="/api/v1", tags=["jobs"])
app.include_router(matches_router, prefix="/api/v1", tags=["matches"])
app.include_router(notifications_router, prefix="/api/v1", tags=["notifications"])

@app.on_event("startup")
async def startup_event():
    start_scheduler()