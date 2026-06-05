from pathlib import Path
from pydantic import BaseModel
import os


class Settings(BaseModel):
    chest_model_path: Path = Path(os.getenv("CHEST_MODEL_PATH", r"F:\visual_project\best_model_resnet18.pth"))
    rag_doc_dir: Path = Path(os.getenv("RAG_DOC_DIR", "docs/knowledge"))
    rag_index_path: Path = Path(os.getenv("RAG_INDEX_PATH", "data/rag_index.pkl"))
    qwen_model_path: str | None = os.getenv("QWEN_MODEL_PATH")
    qwen_load_in_4bit: bool = os.getenv("QWEN_LOAD_IN_4BIT", "0") == "1"


settings = Settings()

