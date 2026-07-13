from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.database import engine
from routers.resume import router as resume_router
from routers.company import router as company_router
from routers.people import router as people_router
from routers.outreach import router as outreach_router

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


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
