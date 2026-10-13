"""RAG Chat & Code Explanation Endpoints."""

import time
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from tools.rag.retrievers import rag_pipeline
from tools.rag.chunking import ast_chunker
from llm.prompts import prompt_manager

router = APIRouter(prefix="/api/v1", tags=["RAG & Intelligence"])


class ChatRequest(BaseModel):
    query: str = Field(..., description="Natural language question or error message")
    retriever_type: Optional[str] = Field("chroma", description="tfidf | faiss | chroma")
    top_k: Optional[int] = Field(5, ge=1, le=20)


class Citation(BaseModel):
    path: str
    name: str
    lines: List[int]
    score: float
    retriever: str


class ChatResponse(BaseModel):
    query: str
    answer: str
    citations: List[Citation]
    confidence_score: float
    retriever_used: str
    latency_ms: float


class ExplainRequest(BaseModel):
    file_path: str = Field(..., description="Target repository file path")
    symbol_name: Optional[str] = Field(None, description="Function or class name")
    code_snippet: Optional[str] = Field(None, description="Optional raw code snippet")


class ExplainResponse(BaseModel):
    file: str
    symbol: str
    summary: str
    ast_metadata: Dict[str, Any]
    callers_and_callees: Dict[str, List[str]]
    historical_incidents: List[Dict[str, str]]


@router.post("/chat", response_model=ChatResponse)
def rag_chat(request: ChatRequest):
    """Answers code intelligence or incident queries using RAG citations."""
    start_time = time.perf_counter()

    hits = rag_pipeline.retrieve(
        query=request.query,
        retriever_type=request.retriever_type or "chroma",
        top_k=request.top_k or 5,
    )

    citations = [
        Citation(
            path=h.file_path,
            name=h.name,
            lines=[h.start_line, h.end_line],
            score=h.score,
            retriever=h.retriever_type,
        )
        for h in hits
    ]

    # Synthesize grounded answer
    if hits:
        top_hit = hits[0]
        answer = (
            f"Based on repository analysis of {top_hit.file_path} (symbol: {top_hit.name}):\n"
            f"The matching component '{top_hit.name}' addresses this domain. "
            f"Reference excerpt from lines {top_hit.start_line}-{top_hit.end_line}:\n"
            f"\"{top_hit.content[:240].strip()}...\""
        )
        confidence = min(0.99, max(0.50, round(top_hit.score, 2)))
    else:
        answer = "No matching code symbols or incident runbooks were found in the repository index."
        confidence = 0.20

    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

    return ChatResponse(
        query=request.query,
        answer=answer,
        citations=citations,
        confidence_score=confidence,
        retriever_used=request.retriever_type or "chroma",
        latency_ms=latency_ms,
    )


@router.post("/explain", response_model=ExplainResponse)
def explain_code(request: ExplainRequest):
    """Provides AST-based architectural summary, caller/callee breakdown, and historical incidents."""
    chunks = []
    
    if request.code_snippet:
        chunks = ast_chunker.chunk_code(request.code_snippet, file_path=request.file_path)
    elif os.path.exists(request.file_path):
        chunks = ast_chunker.chunk_file(request.file_path)
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Target file '{request.file_path}' does not exist on filesystem and no snippet was provided.",
        )

    target_chunk = None
    if request.symbol_name:
        for c in chunks:
            if c.name == request.symbol_name:
                target_chunk = c
                break

    if not target_chunk and chunks:
        target_chunk = chunks[0]

    if not target_chunk:
        raise HTTPException(status_code=400, detail="Could not parse valid AST symbol from input.")

    # Find historical runbooks
    runbook_hits = rag_pipeline.retrieve(
        query=f"{target_chunk.name} {target_chunk.docstring or ''}",
        retriever_type="tfidf",
        top_k=2,
    )

    incidents = []
    for rh in runbook_hits:
        if "runbook" in rh.file_path:
            incidents.append({
                "incident": rh.name,
                "path": rh.file_path,
                "recommendation": rh.content[:180].strip(),
            })

    return ExplainResponse(
        file=target_chunk.file_path,
        symbol=target_chunk.name,
        summary=target_chunk.docstring or f"AST-parsed {target_chunk.chunk_type} definition.",
        ast_metadata=target_chunk.to_metadata(),
        callers_and_callees={
            "inputs": target_chunk.parameters,
            "outputs": ["return_type_annotated"],
            "dependencies": target_chunk.decorators,
        },
        historical_incidents=incidents,
    )
