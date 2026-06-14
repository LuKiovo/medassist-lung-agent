from pathlib import Path

import torch
from fastapi import APIRouter

from medassist_lung_agent.config import settings


router = APIRouter()


@router.get("")
def status():
    doc_count = 0
    if settings.rag_doc_dir.exists():
        doc_count = len([p for p in settings.rag_doc_dir.rglob("*") if p.suffix.lower() in {".txt", ".md"}])

    qwen_mode = "fallback"
    if settings.qwen_model_path:
        qwen_mode = "merged_model"
    elif settings.qwen_base_model_path and settings.qwen_adapter_path:
        qwen_mode = "lora_adapter"

    return {
        "status": "ok",
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "rag": {
            "doc_dir": str(settings.rag_doc_dir),
            "document_count": doc_count,
            "index_exists": settings.rag_index_path.exists(),
        },
        "xray": {
            "model_path": str(settings.chest_model_path),
            "model_exists": settings.chest_model_path.exists(),
        },
        "qwen": {
            "mode": qwen_mode,
            "configured": qwen_mode != "fallback",
            "load_in_4bit": settings.qwen_load_in_4bit,
        },
    }
