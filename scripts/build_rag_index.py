from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from medassist_lung_agent.config import settings
from medassist_lung_agent.rag.indexer import build_index


if __name__ == "__main__":
    index = build_index(settings.rag_doc_dir, settings.rag_index_path)
    print(f"Built RAG index: {len(index.chunks)} chunks -> {settings.rag_index_path}")
