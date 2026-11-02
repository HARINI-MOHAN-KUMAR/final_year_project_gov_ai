"""
RAG (Retrieval-Augmented Generation) module for GovGuide AI.

Uses sentence-transformers to embed scheme knowledge and FAISS
for fast similarity search. Results are used to ground LLM responses.
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

# Lazy imports for heavy dependencies
_sentence_transformers_available = False
_faiss_available = False

try:
    from sentence_transformers import SentenceTransformer
    _sentence_transformers_available = True
except ImportError:
    logger.warning("sentence-transformers not available. RAG will use keyword matching fallback.")

try:
    import faiss
    _faiss_available = True
except ImportError:
    logger.warning("faiss-cpu not available. RAG will use keyword matching fallback.")


class GovGuideRAG:
    """
    RAG engine: embeds scheme descriptions and retrieves relevant context
    based on user query similarity.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._encoder: Optional[object] = None
        self._index: Optional[object] = None
        self._documents: List[Dict] = []  # metadata for each indexed chunk
        self._texts: List[str] = []       # raw text of each chunk
        self._ready = False

    def _get_encoder(self):
        """Lazy-load the sentence transformer model."""
        if self._encoder is None and _sentence_transformers_available:
            logger.info(f"Loading sentence transformer: {self.model_name}")
            self._encoder = SentenceTransformer(self.model_name)
        return self._encoder

    def _scheme_to_text(self, scheme: Dict) -> str:
        """Convert a scheme dict to a rich text chunk for indexing."""
        rules = scheme.get("eligibility_rules", {})
        docs = ", ".join(scheme.get("required_documents", []))
        tags = ", ".join(scheme.get("tags", []))

        text = (
            f"Scheme: {scheme['name']}\n"
            f"Category: {scheme['category']}\n"
            f"Description: {scheme['description']}\n"
            f"Benefits: {scheme['benefits']}\n"
            f"State: {scheme['state_applicability']}\n"
            f"Deadline: {scheme['deadline']}\n"
            f"Required Documents: {docs}\n"
            f"Eligibility: {json.dumps(rules, ensure_ascii=False)}\n"
            f"Tags: {tags}\n"
            f"Official URL: {scheme['official_url']}"
        )
        return text

    def build_index(self, schemes: List[Dict]) -> None:
        """Build FAISS index from scheme documents."""
        self._documents = schemes
        self._texts = [self._scheme_to_text(s) for s in schemes]

        encoder = self._get_encoder()
        if encoder is None or not _faiss_available:
            logger.info("Using keyword matching fallback (no FAISS/encoder).")
            self._ready = True
            return

        logger.info(f"Encoding {len(self._texts)} scheme documents...")
        embeddings = encoder.encode(self._texts, show_progress_bar=False)
        embeddings = embeddings.astype(np.float32)

        # Normalize for cosine similarity
        faiss.normalize_L2(embeddings)

        dim = embeddings.shape[1]
        self._index = faiss.IndexFlatIP(dim)  # Inner Product = cosine after normalization
        self._index.add(embeddings)

        self._ready = True
        logger.info(f"FAISS index built with {self._index.ntotal} vectors (dim={dim})")

    def save_index(self, path: str) -> None:
        """Save FAISS index and metadata to disk."""
        if not _faiss_available or self._index is None:
            return
        os.makedirs(path, exist_ok=True)
        faiss.write_index(self._index, os.path.join(path, "index.faiss"))
        with open(os.path.join(path, "docs.json"), "w", encoding="utf-8") as f:
            json.dump({"documents": self._documents, "texts": self._texts}, f, ensure_ascii=False)
        logger.info(f"FAISS index saved to {path}")

    def load_index(self, path: str) -> bool:
        """Load FAISS index from disk. Returns True on success."""
        faiss_path = os.path.join(path, "index.faiss")
        docs_path = os.path.join(path, "docs.json")
        if not os.path.exists(faiss_path) or not _faiss_available:
            return False
        try:
            self._index = faiss.read_index(faiss_path)
            with open(docs_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._documents = data["documents"]
            self._texts = data["texts"]
            self._ready = True
            logger.info(f"FAISS index loaded from {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load FAISS index: {e}")
            return False

    def _keyword_search(self, query: str, k: int) -> List[Tuple[Dict, str, float]]:
        """Fallback: simple keyword-based search when FAISS is unavailable."""
        query_lower = query.lower()
        scored = []
        for doc, text in zip(self._documents, self._texts):
            score = sum(1 for word in query_lower.split() if word in text.lower())
            scored.append((doc, text, float(score)))
        scored.sort(key=lambda x: x[2], reverse=True)
        return scored[:k]

    def retrieve(self, query: str, k: int = 3) -> List[Dict]:
        """
        Retrieve the top-k most relevant scheme documents for a query.

        Returns list of dicts: {scheme, text, score, source_name}
        """
        if not self._ready or not self._texts:
            return []

        encoder = self._get_encoder()
        if encoder is None or not _faiss_available or self._index is None:
            results = self._keyword_search(query, k)
        else:
            q_emb = encoder.encode([query]).astype(np.float32)
            faiss.normalize_L2(q_emb)
            scores, indices = self._index.search(q_emb, k)
            results = [
                (self._documents[i], self._texts[i], float(scores[0][j]))
                for j, i in enumerate(indices[0])
                if i < len(self._documents)
            ]

        return [
            {
                "scheme_id": doc.get("id"),
                "scheme_name": doc.get("name"),
                "text": text[:600],  # Truncate to avoid token overflow
                "score": round(score, 4),
                "source_url": doc.get("official_url"),
            }
            for doc, text, score in results
        ]

    def get_context_string(self, query: str, k: int = 3) -> Tuple[str, List[Dict]]:
        """
        Return formatted context string and source list for LLM prompt injection.
        """
        sources = self.retrieve(query, k)
        if not sources:
            return "", []

        ctx_parts = []
        for i, src in enumerate(sources, 1):
            ctx_parts.append(
                f"[Source {i}: {src['scheme_name']}]\n{src['text']}"
            )
        context = "\n\n---\n\n".join(ctx_parts)
        return context, sources


# ── Singleton RAG instance ───────────────────────────────────────────────────

_rag_instance: Optional[GovGuideRAG] = None


def get_rag() -> GovGuideRAG:
    """Return (or lazily initialize) the singleton RAG engine."""
    global _rag_instance
    if _rag_instance is None:
        from app.ml.eligibility_engine import get_schemes
        from app.core.config import settings

        _rag_instance = GovGuideRAG(model_name=settings.EMBEDDINGS_MODEL)

        # Try loading a pre-built index
        if not _rag_instance.load_index(settings.FAISS_INDEX_PATH):
            # Build fresh index
            schemes = get_schemes()
            _rag_instance.build_index(schemes)
            _rag_instance.save_index(settings.FAISS_INDEX_PATH)

    return _rag_instance
