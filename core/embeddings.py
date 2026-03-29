"""
NewsGPT Navigator — Embeddings & Vector Store

Sentence-transformers embeddings with FAISS vector store for RAG.
"""

import numpy as np
from typing import Optional

from core.config import settings

_model = None
_index = None
_documents = []


def _get_model():
    """
    Strictly lazy-load the sentence-transformer model as a singleton.
    This ensures no RAM is used until the model is actually needed.
    """
    global _model
    if _model is None:
        print(f"[Embeddings] First Use: Loading {settings.EMBEDDING_MODEL} (RAM expected ~200MB+)...")
        # Local imports ensure this doesn't block app initialization
        try:
            from sentence_transformers import SentenceTransformer
            import torch
            
            # Disable gradients calculation to save memory during inference
            torch.set_grad_enabled(False)
            
            _model = SentenceTransformer(settings.EMBEDDING_MODEL)
            print(f"[Embeddings] Model {settings.EMBEDDING_MODEL} loaded successfully.")
        except Exception as e:
            print(f"[Embeddings] FATAL: Failed to load model: {e}")
            raise RuntimeError(f"Model load failed: {e}")
            
    return _model


def build_index(texts: list[str]) -> bool:
    """
    Build a FAISS index from a list of text documents.

    Args:
        texts: List of document strings to index

    Returns:
        True if index built successfully
    """
    global _index, _documents
    import faiss

    if not texts:
        return False

    try:
        model = _get_model()
        embeddings = model.encode(texts, show_progress_bar=False)
        embeddings = np.array(embeddings, dtype="float32")

        # Normalize for cosine similarity
        faiss.normalize_L2(embeddings)

        # Build index
        dimension = embeddings.shape[1]
        _index = faiss.IndexFlatIP(dimension)  # Inner product (cosine after normalization)
        _index.add(embeddings)
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
    _index = None
    _documents = []
