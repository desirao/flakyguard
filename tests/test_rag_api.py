"""Test FastAPI endpoints for RAG Chat and Code Explanation."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_api_chat_endpoint():
    payload = {
        "query": "How does Sourcegraph fallback to local git grep?",
        "retriever_type": "chroma",
        "top_k": 3,
    }
    response = client.post("/api/v1/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == payload["query"]
    assert len(data["citations"]) > 0
    assert "confidence_score" in data
    assert data["retriever_used"] == "chroma"
    assert data["latency_ms"] >= 0


def test_api_explain_endpoint_with_snippet():
    snippet = '''
def process_refund(order_id: str, amount: float) -> bool:
    """Refund transaction to original credit card."""
    return True
'''
    payload = {
        "file_path": "billing/refund.py",
        "symbol_name": "process_refund",
        "code_snippet": snippet,
    }
    response = client.post("/api/v1/explain", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "process_refund"
    assert "Refund transaction" in data["summary"]
    assert "inputs" in data["callers_and_callees"]
    assert "order_id" in data["callers_and_callees"]["inputs"]
