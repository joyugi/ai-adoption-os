import os

from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = "claude-opus-4-7"

SYSTEM_PROMPT = """You are an internal knowledge assistant for a mid-size enterprise. \
Employees ask you policy and process questions. You operate under strict governance rules:

1. Answer ONLY using the approved sources provided in the user message. Never use outside knowledge.
2. Always cite the source name (e.g., "Source: Employee Handbook") for every claim you make.
3. If the provided sources do not cover the question, say so clearly and recommend the employee \
escalate to the appropriate human owner. Do not guess or extrapolate.
4. For policy-sensitive or high-risk topics (legal, HR incidents, security, contracts), remind the \
employee that human review is required before acting.
5. Keep answers concise, direct, and practical. Use plain language.

Your goal is trusted adoption: employees should be able to rely on your answers precisely because \
you refuse to answer beyond your approved sources."""


def is_available() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def generate_answer(question: str, sources: list[dict]) -> dict | None:
    """Generate a grounded answer from approved sources via Claude.

    Returns {"answer": str, "cache_read_tokens": int} or None on any failure,
    letting the app fall back to retrieval-only display.
    """
    if not is_available():
        return None

    import anthropic

    sources_text = "\n\n".join(
        f"[Source: {s['source']}] (Category: {s['category']}, Risk: {s['risk_level']})\n"
        f"Q: {s['question']}\nA: {s['answer']}"
        for s in sources
    )

    try:
        client = anthropic.Anthropic()
        response = client.messages.create(
            model=os.environ.get("ANTHROPIC_MODEL", DEFAULT_MODEL),
            max_tokens=1024,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Approved sources:\n\n{sources_text}\n\n"
                        f"Employee question: {question}"
                    ),
                }
            ],
        )
        return {
            "answer": response.content[0].text,
            "cache_read_tokens": response.usage.cache_read_input_tokens,
        }
    except anthropic.APIError:
        return None
