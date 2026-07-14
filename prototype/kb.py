from pathlib import Path

import pandas as pd

KB_PATH = Path(__file__).parent / "sample_data" / "knowledge_base.csv"

_kb = None


def load_kb() -> pd.DataFrame:
    global _kb
    if _kb is None:
        _kb = pd.read_csv(KB_PATH)
    return _kb


def build_corpus(kb: pd.DataFrame) -> list[str]:
    # question text weighted 2x — reduces spurious matches on answer-body words
    return (
        kb["question"] + " " + kb["question"] + " "
        + kb["answer"] + " " + kb["category"]
    ).tolist()
