from dataclasses import dataclass
from pathlib import Path
import pickle
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class RagChunk:
    text: str
    source: str


@dataclass
class RagIndex:
    chunks: list[RagChunk]
    vectorizer: TfidfVectorizer
    matrix: object


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _chunk_text(text: str, source: str, max_chars: int = 700, overlap: int = 100) -> list[RagChunk]:
    clean = _normalize(text)
    chunks: list[RagChunk] = []
    start = 0
    while start < len(clean):
        end = min(len(clean), start + max_chars)
        chunk = clean[start:end]
        if len(chunk) > 5:
            chunks.append(RagChunk(text=chunk, source=source))
        if end == len(clean):
            break
        start = max(0, end - overlap)
    return chunks


def load_documents(doc_dir: Path) -> list[RagChunk]:
    chunks: list[RagChunk] = []
    for path in sorted(doc_dir.rglob("*")):
        if path.suffix.lower() not in {".txt", ".md"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        chunks.extend(_chunk_text(text, source=str(path)))
    return chunks


def build_index(doc_dir: Path, index_path: Path) -> RagIndex:
    chunks = load_documents(doc_dir)
    if not chunks:
        raise ValueError(f"No documents found in {doc_dir}")

    vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), max_features=50000)
    matrix = vectorizer.fit_transform([chunk.text for chunk in chunks])
    index = RagIndex(chunks=chunks, vectorizer=vectorizer, matrix=matrix)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with index_path.open("wb") as f:
        pickle.dump(index, f)
    return index


def load_index(index_path: Path) -> RagIndex:
    with index_path.open("rb") as f:
        return pickle.load(f)


def retrieve(query: str, index: RagIndex, top_k: int = 4) -> list[dict]:
    query_vec = index.vectorizer.transform([query])
    sims = cosine_similarity(query_vec, index.matrix).ravel()
    ranked = sims.argsort()[::-1][:top_k]
    return [
        {
            "score": float(sims[i]),
            "source": index.chunks[i].source,
            "text": index.chunks[i].text,
        }
        for i in ranked
        if sims[i] > 0
    ]
