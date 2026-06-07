from pathlib import Path
from pydantic import BaseModel
import os


def _load_dotenv(path: Path = Path(".env")) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


_load_dotenv()


class Settings(BaseModel):
    chest_model_path: Path = Path(os.getenv("CHEST_MODEL_PATH", r"F:\visual_project\best_model_resnet18.pth"))
    rag_doc_dir: Path = Path(os.getenv("RAG_DOC_DIR", "docs/knowledge"))
    rag_index_path: Path = Path(os.getenv("RAG_INDEX_PATH", "data/rag_index.pkl"))
    qwen_model_path: str | None = os.getenv("QWEN_MODEL_PATH")
    qwen_base_model_path: str | None = os.getenv("QWEN_BASE_MODEL_PATH")
    qwen_adapter_path: str | None = os.getenv("QWEN_ADAPTER_PATH")
    qwen_load_in_4bit: bool = os.getenv("QWEN_LOAD_IN_4BIT", "0") == "1"


settings = Settings()
