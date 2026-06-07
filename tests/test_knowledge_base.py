from pathlib import Path


def test_knowledge_base_has_at_least_100_text_files():
    doc_dir = Path("docs/knowledge")
    files = list(doc_dir.glob("*.txt"))
    assert len(files) >= 100

