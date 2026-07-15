from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.database import engine
from routers.resume import router as resume_router
from routers.company import router as company_router
from routers.people import router as people_router
from routers.outreach import router as outreach_router
from routers.graph import router as graph_router
from routers.job import router as job_router
from routers.match import router as match_router
from routers.memory import router as memory_router
from routers.extension import router as extension_router
from routers.daily import router as daily_router
from routers.goal import router as goal_router
from routers.knowledge_graph import router as kg_router
from routers.stats import router as stats_router

app = FastAPI(
    title="CareerOS API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resume_router, prefix="/api/v1")
app.include_router(company_router, prefix="/api/v1")
app.include_router(people_router, prefix="/api/v1")
app.include_router(outreach_router, prefix="/api/v1")
app.include_router(graph_router, prefix="/api/v1")
app.include_router(job_router, prefix="/api/v1")
app.include_router(match_router, prefix="/api/v1")
app.include_router(memory_router, prefix="/api/v1")
app.include_router(extension_router, prefix="/api/v1")
app.include_router(daily_router, prefix="/api/v1")
app.include_router(goal_router, prefix="/api/v1")
app.include_router(kg_router, prefix="/api/v1")
app.include_router(stats_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
