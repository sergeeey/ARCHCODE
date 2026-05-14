"""
Embeddings - Sentence embeddings for hypothesis similarity.

Uses sentence-transformers with caching.
Model: all-MiniLM-L6-v2 (384-dim, fast, good quality)
"""

from pathlib import Path
from typing import List
import logging
import numpy as np
import json

logger = logging.getLogger(__name__)


class EmbeddingEngine:
    """Compute and cache sentence embeddings."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", cache_dir: Path = None):
        self.model_name = model_name
        self.cache_dir = cache_dir or Path("./data/embeddings")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Lazy load model (only when needed)
        self.model = None
        self._cache = {}  # In-memory cache: {text: embedding}

    def _load_model(self):
        """Lazy load sentence-transformers model."""
        if self.model is None:
            from sentence_transformers import SentenceTransformer

            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("✓ Model loaded")

    def embed(self, texts: List[str]) -> np.ndarray:
        """
        Compute embeddings for list of texts.

        Args:
            texts: List of strings to embed

        Returns:
            np.ndarray of shape (len(texts), 384)
        """
        self._load_model()

        # Check cache
        uncached_texts = []
        uncached_indices = []
        embeddings = np.zeros((len(texts), 384))

        for i, text in enumerate(texts):
            if text in self._cache:
                embeddings[i] = self._cache[text]
            else:
                uncached_texts.append(text)
                uncached_indices.append(i)

        # Compute uncached embeddings
        if uncached_texts:
            logger.info(f"Computing {len(uncached_texts)} embeddings...")
            new_embeddings = self.model.encode(uncached_texts, show_progress_bar=False)

            # Update cache
            for text, emb in zip(uncached_texts, new_embeddings):
                self._cache[text] = emb

            # Insert into output array
            for idx, emb in zip(uncached_indices, new_embeddings):
                embeddings[idx] = emb

        return embeddings

    def cosine_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings.

        Args:
            emb1, emb2: Embedding vectors (1D arrays)

        Returns:
            Similarity score in [0, 1]
        """
        # Normalize
        emb1_norm = emb1 / (np.linalg.norm(emb1) + 1e-8)
        emb2_norm = emb2 / (np.linalg.norm(emb2) + 1e-8)

        # Dot product
        return float(np.dot(emb1_norm, emb2_norm))

    def pairwise_similarity(self, embeddings: np.ndarray) -> np.ndarray:
        """
        Compute pairwise cosine similarity matrix.

        Args:
            embeddings: Array of shape (n, 384)

        Returns:
            Similarity matrix of shape (n, n)
        """
        # Normalize rows
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        normalized = embeddings / (norms + 1e-8)

        # Dot product = cosine similarity (when normalized)
        return normalized @ normalized.T

    def save_cache(self):
        """Persist in-memory cache to disk."""
        cache_path = self.cache_dir / "embedding_cache.json"

        # Convert numpy arrays to lists
        serializable_cache = {text: emb.tolist() for text, emb in self._cache.items()}

        with open(cache_path, "w") as f:
            json.dump(serializable_cache, f)

        logger.info(f"✓ Saved {len(self._cache)} embeddings to {cache_path}")

    def load_cache(self):
        """Load cached embeddings from disk."""
        cache_path = self.cache_dir / "embedding_cache.json"

        if not cache_path.exists():
            logger.info("No embedding cache found")
            return

        with open(cache_path) as f:
            serializable_cache = json.load(f)

        # Convert lists back to numpy arrays
        self._cache = {text: np.array(emb) for text, emb in serializable_cache.items()}

        logger.info(f"✓ Loaded {len(self._cache)} embeddings from cache")
