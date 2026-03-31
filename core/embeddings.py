"""
NewsGPT Navigator — Embeddings & Vector Store

Sentence-transformers embeddings with FAISS vector store for RAG.
"""

import numpy as np
from typing import Optional, List, Dict
from core.config import settings

# Global state for vectors
_vectorizer = None
_matrix = None
_documents = []


def _get_vectorizer():
    """Lazy-load the TF-IDF vectorizer."""
    global _vectorizer
    if _vectorizer is None:
        from sklearn.feature_extraction.text import TfidfVectorizer
        _vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=5000,
            ngram_range=(1, 2)
        )
    return _vectorizer


def build_index(texts: List[str]) -> bool:
    """
    Build a TF-IDF index from a list of text documents.
    Replacing FAISS for Render Free Tier (Memory Optimization).
    """
    global _matrix, _documents
    if not texts:
        return False

    try:
        vectorizer = _get_model() # Using the existing _get_model name for compatibility if needed, but better to use _get_vectorizer
        _matrix = _get_vectorizer().fit_transform(texts)
        _documents = texts
        print(f"[Embeddings] Built TF-IDF index with {len(texts)} documents.")
        return True
    except Exception as e:
        print(f"[Embeddings] Error building index: {e}")
        return False


def _get_model():
    """Stub for compatibility with existing calls if any."""
    return _get_vectorizer()


def search(query: str, top_k: int = None) -> List[Dict]:
    """
    Search the TF-IDF index using Cosine Similarity.
    """
    global _matrix, _documents
    if _matrix is None or not _documents:
        return []

    if top_k is None:
        top_k = settings.TOP_K_RESULTS

    try:
        from sklearn.metrics.pairwise import cosine_similarity
        
        vectorizer = _get_vectorizer()
        query_vec = vectorizer.transform([query])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_vec, _matrix).flatten()
        
        # Get top-k indices
        top_indices = similarities.argsort()[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            if score > 0: # Only return relevant matches
                results.append({
                    "text": _documents[idx],
                    "score": score,
                    "index": int(idx),
                })
        
        return results
    except Exception as e:
        print(f"[Embeddings] Search error: {e}")
        return []


def clear_index():
    """Clear the current index and documents."""
    global _matrix, _documents
    _matrix = None
    _documents = []
