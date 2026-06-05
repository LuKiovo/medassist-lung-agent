from fastapi import APIRouter

from medassist_lung_agent.config import settings
from medassist_lung_agent.rag.indexer import build_index


router = APIRouter()


@router.post("/reindex")
def reindex():
    index = build_index(settings.rag_doc_dir, settings.rag_index_path)
    return {
        "status": "ok",
        "documents": len(index.chunks),
        "index_path": str(settings.rag_index_path),
    }

