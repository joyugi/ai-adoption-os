# AI Adoption OS Roadmap

## Product Vision

Help organizations move AI initiatives from pilot to production through trusted workflows, measurable adoption, and practical governance.

V1: Working prototype
V2: Real retrieval + LLM pipeline with persistent telemetry
V3: Semantic retrieval + evaluation pipeline
V4: Adoption intelligence and governance controls

---

## Current Version (V3) — Shipped

### Semantic Retrieval + Evaluation Pipeline

- Semantic retrieval via local model2vec embeddings — matches meaning, not keywords ("can I WFH?" now finds the remote work policy; TF-IDF scored it 0.0)
- Acronym normalization layer for workplace shorthand (WFH, PTO, NDA, …)
- Golden-set evaluation suite (40 cases) scoring hit rate, refusal correctness, confidence calibration, and MRR — TF-IDF vs semantic compared side by side
- Threshold tuning driven by the eval harness, with a documented recall-first trade-off (Claude's grounding prompt is the second gate for out-of-scope questions)
- Claude-as-judge scoring of answer groundedness and citation quality
- Committed, reproducible eval report: hit@1 84% → 100%, keyword-mismatch hit@1 60% → 100%, false refusals 19% → 0%
- TF-IDF retriever retained for eval comparison

### Goal

Prove the product works: measurable retrieval quality, regression-safe changes.

---

## V2 — Shipped

### Real Retrieval + LLM Pipeline

- TF-IDF retrieval with similarity-based confidence scoring
- Claude-generated answers grounded in approved sources, with citations
- Retrieval-only fallback mode when no API key is configured
- Persistent SQLite adoption telemetry with dashboard charts
- Coverage-gap detection and escalation for unanswered questions
- Expanded knowledge base (32 entries, 9 categories, 3 risk levels)

### Goal

Make the product real: trusted answers, honest metrics.

---

## V4 — Candidate Directions

### 1. Adoption Intelligence Layer

Deeper analytics on the existing telemetry: usage trends over time, repeat-usage rate, weekly active users, time-saved rollups, and LLM-vs-fallback answer breakdowns.

Also: Helpful / Not Helpful feedback buttons on answers, feeding the helpful-response-rate metric.

### 2. Governance Controls

- Role-based access controls
- Sensitive query detection
- Escalation workflow for policy-sensitive questions
- Content-owner review queue and approval workflow
- Audit logs

### Goal

Enable safe enterprise deployment with visible adoption evidence.

---

## V5

### Admin & Scale Features

- Multi-team workspaces
- Content management portal
- Connectors to internal docs
- Slack / Teams integration
- SSO support

### Goal

Support production-scale rollout.

---

## Product Principles

- AI success depends on adoption, not model quality alone
- Trust must be designed into workflows
- Human oversight matters
- Measurement drives investment
- Governance should enable progress, not block it

---

## Success Metrics

- Weekly active users
- Repeat usage rate
- Helpful response rate
- Time saved per user
- Reduction in support tickets
- Expansion across teams