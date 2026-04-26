"""
NewsGPT Navigator — Embeddings & Vector Store

Sentence-transformers embeddings with FAISS vector store for RAG.
"""

import numpy as np
import threading
from typing import Optional

from core.config import settings

_model = None
_index = None
_documents = []
_lock = threading.Lock()


def _get_model():
    """Lazy-load the sentence-transformer model."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _model


def build_index(texts: list[str]) -> bool:
    """
    Build a FAISS index from a list of text documents.
    Reuses existing index if documents match.

    Args:
        texts: List of document strings to index

    Returns:
        True if index is ready
    """
    global _index, _documents
    import faiss

    if not texts:
        return False

    with _lock:
        # Check if index already exists and documents match
        if _index is not None and _documents == texts:
            print(f"[Embeddings] Reusing existing index with {len(_documents)} documents.")
            return True

        try:
            model = _get_model()
            embeddings = model.encode(texts, show_progress_bar=False)
            embeddings = np.array(embeddings, dtype="float32")

            # Normalize for cosine similarity
            faiss.normalize_L2(embeddings)

            # Build index
            dimension = embeddings.shape[1]
            new_index = faiss.IndexFlatIP(dimension)  # Inner product (cosine after normalization)
            new_index.add(embeddings)
            
            _index = new_index
            _documents = texts

            print(f"[Embeddings] Built FAISS index with {len(texts)} documents, dim={dimension}")
            return True

        except Exception as e:
            print(f"[Embeddings] Error building index: {e}")
            return False


def search(query: str, top_k: int = None) -> list[dict]:
    """
    Search the FAISS index with a query.

    Args:
        query: Search query string
        top_k: Number of results to return

    Returns:
        List of {text, score, index} dicts
    """
    global _index, _documents
    import faiss

    if _index is None or not _documents:
        return []

    if top_k is None:
        top_k = settings.TOP_K_RESULTS

    top_k = min(top_k, len(_documents))

    try:
        model = _get_model()
        query_embedding = model.encode([query], show_progress_bar=False)
        query_embedding = np.array(query_embedding, dtype="float32")
        faiss.normalize_L2(query_embedding)

        # Search is usually thread-safe for reading
        scores, indices = _index.search(query_embedding, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(_documents):
                results.append({
                    "text": _documents[idx],
                    "score": float(score),
                    "index": int(idx),
                })

        return results

    except Exception as e:
        print(f"[Embeddings] Search error: {e}")
        return []


def clear_index():
    """Clear the current index and documents."""
    global _index, _documents
    with _lock:
        _index = None
        _documents = []
