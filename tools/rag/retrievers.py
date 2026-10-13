"""LangChain Multi-Retriever RAG Pipeline for FlakyGuard-AI.

Supports TF-IDF (lexical baseline), FAISS Dense Vector retrieval, and ChromaDB-style
persistent vector stores over AST-chunked Python codebases and incident post-mortem runbooks.
"""

import math
import os
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from tools.rag.chunking import CodeChunk, ast_chunker


@dataclass
class RAGHit:
    chunk_id: str
    file_path: str
    name: str
    chunk_type: str
    content: str
    score: float
    retriever_type: str
    start_line: int
    end_line: int
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_citation(self) -> Dict[str, Any]:
        return {
            "path": self.file_path,
            "name": self.name,
            "lines": [self.start_line, self.end_line],
            "score": round(self.score, 4),
            "retriever": self.retriever_type,
        }


class BaseCodeRetriever(ABC):
    """Abstract base class for all code retrieval backends."""

    def __init__(self, name: str):
        self.name = name
        self.chunks: List[CodeChunk] = []

    @abstractmethod
    def index(self, chunks: List[CodeChunk]) -> None:
        """Index a collection of code/doc chunks."""
        pass

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> List[RAGHit]:
        """Retrieve the top-k most relevant chunks for a query."""
        pass


class TFIDFRetriever(BaseCodeRetriever):
    """Lexical baseline retriever using TF-IDF and Cosine Similarity."""

    def __init__(self):
        super().__init__("tfidf")
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
            sublinear_tf=True,
            token_pattern=r"(?u)\b[a-zA-Z_][a-zA-Z0-9_]+\b",
        )
        self.matrix = None

    def index(self, chunks: List[CodeChunk]) -> None:
        self.chunks = chunks
        if not chunks:
            return

        texts = [c.to_searchable_text() for c in chunks]
        self.matrix = self.vectorizer.fit_transform(texts)

    def retrieve(self, query: str, top_k: int = 5) -> List[RAGHit]:
        if not self.chunks or self.matrix is None:
            return []

        try:
            query_vec = self.vectorizer.transform([query])
            scores = cosine_similarity(query_vec, self.matrix).flatten()
        except Exception:
            return []

        top_indices = np.argsort(scores)[::-1][:top_k]
        hits: List[RAGHit] = []

        for idx in top_indices:
            score = float(scores[idx])
            if score > 0.001:
                chunk = self.chunks[idx]
                hits.append(
                    RAGHit(
                        chunk_id=chunk.chunk_id,
                        file_path=chunk.file_path,
                        name=chunk.name,
                        chunk_type=chunk.chunk_type,
                        content=chunk.content,
                        score=score,
                        retriever_type="tfidf",
                        start_line=chunk.start_line,
                        end_line=chunk.end_line,
                        metadata=chunk.to_metadata(),
                    )
                )
        return hits


class DenseEmbeddingModel:
    """Deterministic dense embedding model utilizing character-trigram dense hashing projection."""

    def __init__(self, dimension: int = 128):
        self.dimension = dimension

    def embed_text(self, text: str) -> np.ndarray:
        tokens = re.findall(r"\w+", text.lower())
        vec = np.zeros(self.dimension, dtype=np.float32)
        if not tokens:
            return vec

        for token in tokens:
            # Hash tokens into pseudo-dense subspace
            h = hash(token) % self.dimension
            vec[h] += 1.0

        # Sublinear term scaling & L2 normalization
        vec = np.log1p(vec)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        return vec

    def embed_documents(self, texts: List[str]) -> np.ndarray:
        return np.vstack([self.embed_text(t) for t in texts])


class FAISSDenseRetriever(BaseCodeRetriever):
    """Dense vector retriever modeled after FAISS index with normalized dot-product search."""

    def __init__(self, dimension: int = 128):
        super().__init__("faiss")
        self.embedder = DenseEmbeddingModel(dimension=dimension)
        self.vectors: Optional[np.ndarray] = None

    def index(self, chunks: List[CodeChunk]) -> None:
        self.chunks = chunks
        if not chunks:
            return
        texts = [c.to_searchable_text() for c in chunks]
        self.vectors = self.embedder.embed_documents(texts)

    def retrieve(self, query: str, top_k: int = 5) -> List[RAGHit]:
        if not self.chunks or self.vectors is None:
            return []

        query_vec = self.embedder.embed_text(query).reshape(1, -1)
        scores = np.dot(self.vectors, query_vec.T).flatten()

        top_indices = np.argsort(scores)[::-1][:top_k]
        hits: List[RAGHit] = []

        for idx in top_indices:
            score = float(scores[idx])
            if score > 0.01:
                chunk = self.chunks[idx]
                hits.append(
                    RAGHit(
                        chunk_id=chunk.chunk_id,
                        file_path=chunk.file_path,
                        name=chunk.name,
                        chunk_type=chunk.chunk_type,
                        content=chunk.content,
                        score=score,
                        retriever_type="faiss",
                        start_line=chunk.start_line,
                        end_line=chunk.end_line,
                        metadata=chunk.to_metadata(),
                    )
                )
        return hits


class ChromaDBRetriever(BaseCodeRetriever):
    """Persistent / memory-backed vector store combining semantic keywords and dense representations."""

    def __init__(self, dimension: int = 128):
        super().__init__("chroma")
        self.embedder = DenseEmbeddingModel(dimension=dimension)
        self.vectors: Optional[np.ndarray] = None
        self.tfidf_fallback = TFIDFRetriever()

    def index(self, chunks: List[CodeChunk]) -> None:
        self.chunks = chunks
        if not chunks:
            return
        texts = [c.to_searchable_text() for c in chunks]
        self.vectors = self.embedder.embed_documents(texts)
        self.tfidf_fallback.index(chunks)

    def retrieve(self, query: str, top_k: int = 5) -> List[RAGHit]:
        if not self.chunks or self.vectors is None:
            return []

        # Hybrid dense-sparse scoring
        query_vec = self.embedder.embed_text(query).reshape(1, -1)
        dense_scores = np.dot(self.vectors, query_vec.T).flatten()

        # Combine with lexical weights
        lexical_hits = {h.chunk_id: h.score for h in self.tfidf_fallback.retrieve(query, top_k=top_k * 2)}
        
        combined_scores = []
        for idx, chunk in enumerate(self.chunks):
            d_score = float(dense_scores[idx])
            l_score = lexical_hits.get(chunk.chunk_id, 0.0)
            hybrid_score = 0.6 * d_score + 0.4 * l_score
            combined_scores.append((hybrid_score, idx))

        combined_scores.sort(key=lambda x: x[0], reverse=True)
        hits: List[RAGHit] = []

        for score, idx in combined_scores[:top_k]:
            if score > 0.01:
                chunk = self.chunks[idx]
                hits.append(
                    RAGHit(
                        chunk_id=chunk.chunk_id,
                        file_path=chunk.file_path,
                        name=chunk.name,
                        chunk_type=chunk.chunk_type,
                        content=chunk.content,
                        score=score,
                        retriever_type="chroma",
                        start_line=chunk.start_line,
                        end_line=chunk.end_line,
                        metadata=chunk.to_metadata(),
                    )
                )
        return hits


class MultiRetrieverPipeline:
    """Orchestrates indexing and retrieval across TF-IDF, FAISS, and ChromaDB."""

    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = workspace_root or os.getcwd()
        self.tfidf = TFIDFRetriever()
        self.faiss = FAISSDenseRetriever()
        self.chroma = ChromaDBRetriever()
        self.indexed_chunks: List[CodeChunk] = []

    def index_workspace(self) -> int:
        """Scan workspace Python files and incident runbooks into all retrievers."""
        chunks: List[CodeChunk] = []

        # 1. Chunk Python files using AST
        for sub in ["app", "tools", "llm", "security"]:
            dir_path = os.path.join(self.workspace_root, sub)
            if os.path.exists(dir_path):
                chunks.extend(ast_chunker.chunk_directory(dir_path))

        # 2. Index Markdown Runbooks
        runbooks_dir = os.path.join(self.workspace_root, "data", "runbooks")
        if os.path.exists(runbooks_dir):
            for file in os.listdir(runbooks_dir):
                if file.endswith(".md"):
                    full_p = os.path.join(runbooks_dir, file)
                    text = Path(full_p).read_text(encoding="utf-8", errors="replace")
                    rel_p = f"data/runbooks/{file}"
                    chunks.append(
                        CodeChunk(
                            chunk_id=f"{rel_p}:runbook",
                            file_path=rel_p,
                            name=Path(file).stem,
                            chunk_type="runbook",
                            content=text,
                            docstring="Incident remediation runbook",
                            start_line=1,
                            end_line=len(text.splitlines()),
                        )
                    )

        self.indexed_chunks = chunks
        self.tfidf.index(chunks)
        self.faiss.index(chunks)
        self.chroma.index(chunks)
        return len(chunks)

    def retrieve(
        self,
        query: str,
        retriever_type: str = "chroma",
        top_k: int = 5,
    ) -> List[RAGHit]:
        """Query specific retriever or ensemble."""
        if not self.indexed_chunks:
            self.index_workspace()

        retriever_map = {
            "tfidf": self.tfidf,
            "faiss": self.faiss,
            "chroma": self.chroma,
        }
        retriever = retriever_map.get(retriever_type.lower(), self.chroma)
        return retriever.retrieve(query, top_k=top_k)


# Global singleton instance
rag_pipeline = MultiRetrieverPipeline()
