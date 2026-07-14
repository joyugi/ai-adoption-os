# Changelog

## v3.0.0 - Semantic Retrieval + Evaluation Pipeline

### Added
- Semantic retrieval using local model2vec embeddings (`prototype/retrieval_semantic.py`) — matches meaning rather than keywords; "Can I WFH?" now retrieves the remote work policy (TF-IDF scored it 0.0)
- Acronym normalization for workplace shorthand (WFH, PTO, OOO, NDA, SSO, MFA, 2FA) applied before embedding
- Golden-set evaluation harness (`evals/run_eval.py`, 40 cases) scoring hit@1/hit@3, MRR, refusal correctness, and confidence calibration for both retrievers, with a threshold-tuning sweep
- Claude-as-judge answer scoring for groundedness and citations (`evals/judge.py`), auto-skipped without an API key
- Committed evaluation report (`evals/results/eval_report.md`): hit@1 84% → 100%, keyword-mismatch hit@1 60% → 100%, false refusals 19% → 0%

### Changed
- App retrieval engine switched from TF-IDF to semantic embeddings via a retriever facade (`prototype/retrieval.py`); TF-IDF retained for eval comparison (`prototype/retrieval_tfidf.py`)
- Confidence thresholds tuned on the golden set with a recall-first policy — Claude's grounding prompt serves as the second gate for out-of-scope questions that pass retrieval
- KB loading and corpus construction extracted to `prototype/kb.py`, shared by both retrievers

---

## v2.0.0 - Real Retrieval + LLM Pipeline

### Added
- TF-IDF retrieval with cosine similarity over the knowledge base (`prototype/retrieval.py`)
- Claude-generated grounded answers with source citations and governance system prompt (`prototype/llm.py`)
- Retrieval-only fallback mode when no API key is configured — demo stays runnable
- Persistent SQLite telemetry that survives restarts (`prototype/telemetry.py`)
- Telemetry dashboard charts (actions breakdown, usage by category) and top-unanswered-questions view
- Expanded knowledge base from 5 to 32 entries across 9 categories with Low/Medium/High risk levels
- `.env.example` for API key configuration

### Fixed
- Confidence label now derives from retrieval similarity score instead of mirroring the risk level
- Knowledge base path no longer depends on the working directory
- Run instructions now point at the correct `requirements.txt`

### Removed
- Unused `openai` and `pydantic` dependencies
- Stale `README-backup.md`

---

## v1.0.0 - Initial Portfolio Release

### Added
- Built Streamlit prototype for an internal AI knowledge assistant
- Added sample policy and process knowledge base
- Added basic answer-matching logic
- Added interaction event logging to support adoption telemetry
- Added AI adoption readiness scorecard
- Added product strategy, rollout, governance, and metrics case-study documents
- Added screenshots showing prototype experience and adoption telemetry

### Product Focus
- Demonstrates how AI pilots can move toward production through workflow design, governance, measurement, and user trust

---

## Planned

### v1.1.0 - Trust and Feedback Improvements
- Add user feedback buttons for Helpful / Not Helpful
- Display source references more prominently
- Add unanswered-question capture
- Improve answer relevance and confidence indicators

### v1.2.0 - Adoption Metrics Layer
- Add usage analytics dashboard
- Track repeated usage patterns
- Surface top unanswered questions
- Add team-level adoption metrics

### v2.0.0 - Governance and Scale
- Add escalation paths for high-risk questions
- Add content owner review workflow
- Add role-based governance model
- Explore Slack or Teams integration