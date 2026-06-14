from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from medassist_lung_agent.api.chat import router as chat_router
from medassist_lung_agent.api.xray import router as xray_router
from medassist_lung_agent.api.rag import router as rag_router
from medassist_lung_agent.api.status import router as status_router

STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(
    title="MedAssist Lung Agent",
    description="肺部 X 光辅助诊断 + 日常健康咨询 RAG agent",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
app.include_router(xray_router, prefix="/api/xray", tags=["xray"])
app.include_router(rag_router, prefix="/api/rag", tags=["rag"])
app.include_router(status_router, prefix="/api/status", tags=["status"])

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
