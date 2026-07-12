# Changelog

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