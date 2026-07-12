from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

KB_PATH = Path(__file__).parent / "sample_data" / "knowledge_base.csv"

HIGH_CONFIDENCE_THRESHOLD = 0.45
MEDIUM_CONFIDENCE_THRESHOLD = 0.16

_kb = None
_vectorizer = None
_kb_matrix = None


def _ensure_index():
    global _kb, _vectorizer, _kb_matrix
    if _kb is None:
        _kb = pd.read_csv(KB_PATH)
        # question text weighted 2x — reduces spurious matches on answer-body words
        corpus = (
            _kb["question"] + " " + _kb["question"] + " "
            + _kb["answer"] + " " + _kb["category"]
        ).tolist()
        _vectorizer = TfidfVectorizer(
            stop_words="english", ngram_range=(1, 2), sublinear_tf=True
        )
        _kb_matrix = _vectorizer.fit_transform(corpus)


def load_kb() -> pd.DataFrame:
    _ensure_index()
    return _kb


def search(query: str, top_k: int = 3) -> list[tuple[pd.Series, float]]:
    """Return the top_k KB rows most similar to the query, with cosine scores."""
    _ensure_index()
    query_vec = _vectorizer.transform([query])
    scores = cosine_similarity(query_vec, _kb_matrix).flatten()
    top_indices = scores.argsort()[::-1][:top_k]
    return [(_kb.iloc[i], float(scores[i])) for i in top_indices]


def confidence_label(score: float) -> str | None:
    """Map a retrieval similarity score to a confidence label. None = no reliable match."""
    if score >= HIGH_CONFIDENCE_THRESHOLD:
        return "High"
    if score >= MEDIUM_CONFIDENCE_THRESHOLD:
        return "Medium"
    return None
