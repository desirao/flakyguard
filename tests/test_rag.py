"""Test multi-retriever RAG pipeline (TF-IDF, FAISS, ChromaDB)."""

from tools.rag.chunking import CodeChunk
from tools.rag.retrievers import (
    TFIDFRetriever,
    FAISSDenseRetriever,
    ChromaDBRetriever,
    MultiRetrieverPipeline,
)


def sample_chunks():
    return [
        CodeChunk(
            chunk_id="auth.py:verify_token",
            file_path="auth.py",
            name="verify_token",
            chunk_type="function",
            content="def verify_token(token: str) -> bool:\n    return len(token) > 10",
            docstring="Validates user authentication JWT token.",
            start_line=1,
            end_line=2,
            parameters=["token"],
        ),
        CodeChunk(
            chunk_id="checkout.py:process_cart",
            file_path="checkout.py",
            name="process_cart",
            chunk_type="function",
            content="def process_cart(cart):\n    if not cart: raise ValueError('Empty')\n    return cart.id",
            docstring="Processes user items in cart and charges credit card.",
            start_line=1,
            end_line=3,
            parameters=["cart"],
        ),
        CodeChunk(
            chunk_id="runbooks:socket_timeout.md",
            file_path="data/runbooks/runbook_socket_timeout.md",
            name="runbook_socket_timeout",
            chunk_type="runbook",
            content="Incident Runbook: Socket Timeout in external service calls. Wrap in timeout=(3.05, 10.0).",
            docstring="Runbook for network socket timeouts and HTTPAdapter.",
            start_line=1,
            end_line=2,
        ),
    ]


def test_tfidf_retriever():
    retriever = TFIDFRetriever()
    retriever.index(sample_chunks())
    hits = retriever.retrieve("JWT authentication token", top_k=2)
    assert len(hits) > 0
    assert hits[0].name == "verify_token"
    assert hits[0].retriever_type == "tfidf"


def test_faiss_dense_retriever():
    retriever = FAISSDenseRetriever()
    retriever.index(sample_chunks())
    hits = retriever.retrieve("socket connection timeout retry", top_k=2)
    assert len(hits) > 0
    assert "timeout" in hits[0].name.lower() or "timeout" in hits[0].content.lower()
    assert hits[0].retriever_type == "faiss"


def test_chroma_hybrid_retriever():
    retriever = ChromaDBRetriever()
    retriever.index(sample_chunks())
    hits = retriever.retrieve("process cart charges", top_k=2)
    assert len(hits) > 0
    assert hits[0].name == "process_cart"
    assert hits[0].retriever_type == "chroma"


def test_multi_retriever_pipeline_indexing():
    pipeline = MultiRetrieverPipeline()
    count = pipeline.index_workspace()
    assert count > 0
    hits = pipeline.retrieve("SourcegraphClient", retriever_type="chroma", top_k=3)
    assert len(hits) > 0
    citation = hits[0].to_citation()
    assert "path" in citation
    assert "score" in citation
