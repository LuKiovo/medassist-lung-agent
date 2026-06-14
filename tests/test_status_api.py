from fastapi.testclient import TestClient

from medassist_lung_agent.main import app


def test_status_endpoint_reports_rag_and_qwen_state():
    client = TestClient(app)
    resp = client.get("/api/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["rag"]["document_count"] >= 100
    assert "qwen" in data

