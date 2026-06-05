from pathlib import Path
from urllib.parse import urlparse
import re

import requests
from bs4 import BeautifulSoup


def slugify_url(url: str) -> str:
    parsed = urlparse(url)
    raw = f"{parsed.netloc}{parsed.path}".strip("/")
    return re.sub(r"[^a-zA-Z0-9._-]+", "_", raw)[:120] or "medical_doc"


def fetch_to_text(url: str) -> tuple[str, str]:
    resp = requests.get(url, timeout=20, headers={"User-Agent": "MedAssistRAG/0.1"})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()
    title = soup.title.get_text(" ", strip=True) if soup.title else url
    body = soup.get_text("\n", strip=True)
    return title, body


def save_url_as_txt(url: str, output_dir: Path) -> Path:
    title, body = fetch_to_text(url)
    output_dir.mkdir(parents=True, exist_ok=True)
    out = output_dir / f"{slugify_url(url)}.txt"
    out.write_text(f"标题: {title}\n来源: {url}\n\n{body}\n", encoding="utf-8")
    return out

