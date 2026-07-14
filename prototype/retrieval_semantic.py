import os
import re

import numpy as np
import pandas as pd
from model2vec import StaticModel

from kb import build_corpus, load_kb

MODEL_NAME = os.environ.get("EMBEDDING_MODEL", "minishlab/potion-base-8M")

# Tuned on evals/golden_set.csv (2026-07-13). Semantic scores overlap between
# answerable and off-KB queries, so MEDIUM is set recall-first: every answerable
# case scores >= 0.315 while 4/8 off-KB cases stay below 0.29; the LLM grounding
# prompt is the second gate for off-KB queries that pass retrieval. HIGH = 0.55
# gives 100% top-1 precision (strongest off-KB scorer: 0.514).
HIGH_CONFIDENCE_THRESHOLD = 0.55
MEDIUM_CONFIDENCE_THRESHOLD = 0.29

# Static embeddings miss bare workplace acronyms ("can I WFH?" ranks 8th,
# "can I work from home?" ranks 1st) — expand them before embedding.
ACRONYMS = {
    "wfh": "work from home",
    "pto": "paid time off",
    "ooo": "out of office",
    "nda": "non-disclosure agreement",
    "sso": "single sign-on",
    "mfa": "multi-factor authentication",
    "2fa": "two-factor authentication",
}

_model = None
_kb_matrix = None


def expand_query(query: str) -> str:
    def replace(match: re.Match) -> str:
        return ACRONYMS[match.group(0).lower()]

    pattern = r"\b(" + "|".join(re.escape(a) for a in ACRONYMS) + r")\b"
    return re.sub(pattern, replace, query, flags=re.IGNORECASE)


def _normalize(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    return matrix / np.where(norms == 0, 1.0, norms)


def _ensure_index():
    global _model, _kb_matrix
    if _model is None:
        _model = StaticModel.from_pretrained(MODEL_NAME)
        corpus = build_corpus(load_kb())
        _kb_matrix = _normalize(_model.encode(corpus))


def search(query: str, top_k: int = 3) -> list[tuple[pd.Series, float]]:
    """Return the top_k KB rows most similar to the query, with cosine scores."""
    _ensure_index()
    kb = load_kb()
    query_vec = _normalize(_model.encode([expand_query(query)]))
    scores = (_kb_matrix @ query_vec[0]).flatten()
    top_indices = scores.argsort()[::-1][:top_k]
    return [(kb.iloc[i], float(scores[i])) for i in top_indices]


def confidence_label(score: float) -> str | None:
    """Map a retrieval similarity score to a confidence label. None = no reliable match."""
    if score >= HIGH_CONFIDENCE_THRESHOLD:
        return "High"
    if score >= MEDIUM_CONFIDENCE_THRESHOLD:
        return "Medium"
    return None
