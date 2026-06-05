from pathlib import Path

from medassist_lung_agent.rag.indexer import build_index, retrieve


def test_rag_retrieves_seed_docs(tmp_path: Path):
    doc_dir = tmp_path / "docs"
    doc_dir.mkdir()
    (doc_dir / "fever.txt").write_text("发热可以补液休息。对乙酰氨基酚可退热。", encoding="utf-8")
    index = build_index(doc_dir, tmp_path / "index.pkl")
    hits = retrieve("发热可以退热吗", index, top_k=1)
    assert hits
    assert "退热" in hits[0]["text"] or "发热" in hits[0]["text"]
