from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.documents import router as documents_router
from app.api.search import router as search_router
from app.api.research import router as research_router
from app.db.session import engine


app = FastAPI(
    title="NEXUS API",
    description="Evidence-aware Agentic Decision Intelligence Platform",
    version="0.1.0",
)


app.include_router(documents_router)
app.include_router(search_router)
app.include_router(research_router)


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

        result = connection.execute(
            text("SELECT 1")
        )

        return {
            "database": "connected",
            "result": result.scalar(),
        }