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


QUERY_EXPANSIONS = {
    "高烧": "发热 退热 退烧药 对乙酰氨基酚 布洛芬 体温 成人 儿童",
    "退烧": "发热 退热 退烧药 对乙酰氨基酚 布洛芬 体温",
    "退热": "发热 退烧药 对乙酰氨基酚 布洛芬 体温",
    "发烧": "发热 退热 退烧药 对乙酰氨基酚 布洛芬 体温",
    "肠胃炎": "急性胃肠炎 腹泻 呕吐 腹痛 口服补液盐 脱水",
    "胃肠炎": "急性胃肠炎 腹泻 呕吐 腹痛 口服补液盐 脱水",
    "腹泻": "急性胃肠炎 口服补液盐 脱水 血便 高热",
    "螃蟹": "海鲜 西瓜 食物相克 过敏 胃肠不适 痛风",
    "西瓜": "螃蟹 海鲜 食物相克 胃肠不适",
    "胸片": "胸部 X 光 肺炎 AI 局限 医生阅片",
    "x光": "胸部 X 光 肺炎 AI 局限 医生阅片",
    "咳嗽": "普通感冒 肺炎 咳痰 胸痛 呼吸困难",
}


DOMAIN_KEYWORDS = [
    "发热",
    "退热",
    "退烧药",
    "对乙酰氨基酚",
    "布洛芬",
    "胃肠炎",
    "腹泻",
    "呕吐",
    "螃蟹",
    "西瓜",
    "海鲜",
    "肺炎",
    "胸片",
    "胸部 X 光",
    "呼吸困难",
    "胸痛",
]


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def expand_query(query: str) -> str:
    expanded = [query]
    lower_query = query.lower()
    for key, value in QUERY_EXPANSIONS.items():
        if key in lower_query or key in query:
            expanded.append(value)
    return " ".join(expanded)


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
    expanded_query = expand_query(query)
    query_vec = index.vectorizer.transform([expanded_query])
    sims = cosine_similarity(query_vec, index.matrix).ravel()
    reranked: list[tuple[float, int]] = []
    for i, sim in enumerate(sims):
        text = index.chunks[i].text
        source = index.chunks[i].source
        keyword_hits = sum(1 for kw in DOMAIN_KEYWORDS if kw in expanded_query and kw in text)
        source_bonus = 0.08 if any(token in source.lower() for token in ["fever", "gastro", "crab", "xray", "pneumonia"]) else 0.0
        reranked.append((float(sim) + keyword_hits * 0.12 + source_bonus, i))
    ranked = [i for _, i in sorted(reranked, reverse=True)[:top_k]]
    return [
        {
            "score": float(sims[i]),
            "source": index.chunks[i].source,
            "text": index.chunks[i].text,
        }
        for i in ranked
        if sims[i] > 0
    ]
