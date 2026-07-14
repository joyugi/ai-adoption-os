"""Facade over the available retrieval engines.

app.py imports this module unchanged; the default engine is selected here.
"""

import retrieval_semantic
import retrieval_tfidf
from kb import load_kb

RETRIEVERS = {
    "semantic": retrieval_semantic,
    "tfidf": retrieval_tfidf,
}

DEFAULT_RETRIEVER = "semantic"

_engine = RETRIEVERS[DEFAULT_RETRIEVER]

search = _engine.search
confidence_label = _engine.confidence_label
