import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import router
from .repositories.documents import DocumentsRepository
from .services.ai_provider import AIProvider
from .services.answers import AnswerService
from .services.documents import DocumentService

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    repository = DocumentsRepository()
    await run_in_threadpool(repository.initialize)
    ai = AIProvider()
    try:
        app.state.documents = DocumentService(repository, ai)
        app.state.answers = AnswerService(repository, ai)
        yield
    finally:
        await ai.close()


app = FastAPI(title="DocMind", docs_url="/api/docs", redoc_url=None, lifespan=lifespan)
app.include_router(router)

origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "").split(",")
    if origin.strip()
]
if origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["Content-Type"],
    )
