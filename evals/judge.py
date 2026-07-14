"""Claude-as-judge for answer groundedness and citation quality.

For each answerable golden case, the semantic retriever's sources are fed to
the production answer pipeline (prototype/llm.py), and a separate judge call
scores whether the answer stays within the sources and cites them.
Skipped entirely when no API key is configured.
"""

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent.parent / "prototype"))

import llm
import retrieval_semantic

DEFAULT_MODEL = "claude-opus-4-7"

JUDGE_SYSTEM_PROMPT = """You are an evaluation judge for an enterprise knowledge \
assistant. You will be shown approved sources, an employee question, and the \
assistant's answer. Score the answer on two criteria:

1. grounded: true if every factual claim in the answer is supported by the provided \
sources; false if the answer adds facts, policies, numbers, or advice not present in them. \
Refusing to answer and recommending escalation counts as grounded.
2. cited: true if the answer explicitly names at least one source it drew from.

Respond with ONLY a JSON object, no other text:
{"grounded": true|false, "cited": true|false, "issue": "<one short sentence if either is false, else empty string>"}"""


def is_available() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def _judge_one(client, question: str, answer: str, sources_text: str) -> dict | None:
    import anthropic

    try:
        response = client.messages.create(
            model=os.environ.get("ANTHROPIC_MODEL", DEFAULT_MODEL),
            max_tokens=256,
            system=[
                {
                    "type": "text",
                    "text": JUDGE_SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Approved sources:\n\n{sources_text}\n\n"
                        f"Employee question: {question}\n\n"
                        f"Assistant answer:\n{answer}"
                    ),
                }
            ],
        )
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.strip("`").removeprefix("json").strip()
        verdict = json.loads(raw)
        if not isinstance(verdict.get("grounded"), bool) or not isinstance(
            verdict.get("cited"), bool
        ):
            return None
        return verdict
    except (anthropic.APIError, json.JSONDecodeError):
        return None


def run_judge(semantic_results: list[dict]) -> dict | None:
    """Judge answers for all answerable cases. Returns aggregate rates, or None
    when no API key is configured."""
    if not is_available():
        print("\n--judge skipped: no ANTHROPIC_API_KEY configured.")
        return None

    import anthropic

    client = anthropic.Anthropic()
    answerable = [r for r in semantic_results if r["answerable"]]

    judged = []
    issues = []
    for r in answerable:
        ranked = retrieval_semantic.search(r["query"], top_k=3)
        sources = [row.to_dict() for row, score in ranked
                   if retrieval_semantic.confidence_label(score) is not None]
        if not sources:
            continue
        answer = llm.generate_answer(r["query"], sources)
        if answer is None:
            continue
        sources_text = "\n\n".join(
            f"[Source: {s['source']}] (Category: {s['category']}, Risk: {s['risk_level']})\n"
            f"Q: {s['question']}\nA: {s['answer']}"
            for s in sources
        )
        verdict = _judge_one(client, r["query"], answer["answer"], sources_text)
        if verdict is None:
            continue
        judged.append(verdict)
        if verdict["issue"]:
            issues.append((r["id"], verdict["issue"]))
        print(f"  judged {r['id']}: grounded={verdict['grounded']} cited={verdict['cited']}")

    if not judged:
        print("\n--judge produced no verdicts (API failures?).")
        return None

    return {
        "n": len(judged),
        "grounded_rate": sum(v["grounded"] for v in judged) / len(judged),
        "cited_rate": sum(v["cited"] for v in judged) / len(judged),
        "issues": issues,
    }
