# AI Adoption OS Roadmap

## Product Vision

Help organizations move AI initiatives from pilot to production through trusted workflows, measurable adoption, and practical governance.

V1: Working prototype
V2: Add user feedback capture
V3: Add adoption telemetry dashboard
V4: Add admin governance controls

---

## Current Version (V2) — Shipped

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

## V3 — Candidate Directions (Under Evaluation)

Four directions are being weighed, each with distinct tradeoffs:

### 1. Semantic Retrieval

Replace TF-IDF with vector embeddings so retrieval matches meaning rather than keywords (e.g., "can I WFH?" should match the remote work policy). Fixes the known synonym limitation of keyword retrieval.

### 2. Evaluation Pipeline

A golden-question test suite scoring retrieval hit rate, answer groundedness, refusal correctness for out-of-scope questions, and escalation quality — run on every change. Makes system quality measurable and regression-safe.

### 3. Adoption Intelligence Layer

Deeper analytics on the existing telemetry: usage trends over time, repeat-usage rate, weekly active users, time-saved rollups, and LLM-vs-fallback answer breakdowns.

### 4. Governance Controls

Role-based views, sensitive-query detection, a content-owner review queue for escalated questions, and audit logging.

### Leading Candidate

Options 1 + 2 together: the evaluation suite provides before/after evidence that semantic retrieval outperforms keyword retrieval, turning an infrastructure change into a measurable product improvement.

---

## V4

### Governance Controls

- Role-based access controls
- Sensitive query detection
- Escalation workflow for policy-sensitive questions
- Content approval workflow
- Audit logs

### Goal

Enable safe enterprise deployment.

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