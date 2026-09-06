from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.intelligence import router as intelligence_router
from app.api.decisions import router as decisions_router
from app.api.reports import router as reports_router
from app.api.analytics import router as analytics_router
from app.api.documents import router as documents_router
from app.api.search import router as search_router
from app.api.research import router as research_router
from app.api.knowledge import router as knowledge_router
from app.db.session import engine


app = FastAPI(
    title="NEXUS API",
    description="Evidence-aware Agentic Decision Intelligence Platform",
    version="0.1.0",
)


# API routers
app.include_router(documents_router)
app.include_router(search_router)
app.include_router(research_router)
app.include_router(decisions_router)
app.include_router(reports_router)
app.include_router(analytics_router)
app.include_router(knowledge_router)
app.include_router(intelligence_router)


# Frontend CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "name": "NEXUS",
        "status": "online",
        "version": "0.1.0",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
    }


@app.get("/health/database")
async def database_health():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))

        return {
            "database": "connected",
            "result": result.scalar(),
        }