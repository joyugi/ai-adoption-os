# Retrieval Evaluation Report

- Date: 2026-07-13
- Golden set: golden_set.csv (40 cases: 32 answerable, 8 off-KB)
- Embedding model: minishlab/potion-base-8M
- Thresholds — TF-IDF: High ≥0.45, Medium ≥0.16; Semantic: High ≥0.55, Medium ≥0.29

## Overall comparison

| Metric | tfidf | semantic |
|---|---|---|
| Hit@1 (32 answerable) | 84% | 100% |
| Hit@3 | 88% | 100% |
| MRR | 0.86 | 1.00 |
| Correct refusal (8 off-KB) | 50% | 50% |
| False refusal (answerable) | 19% | 0% |

## Hit@1 by case type

| Case type | n | tfidf | semantic |
|---|---|---|---|
| verbatim | 9 | 100% | 100% |
| paraphrase | 13 | 92% | 100% |
| keyword_mismatch | 10 | 60% | 100% |

## Confidence calibration (top-1 accuracy per label)

**tfidf**

| Label | n | Top-1 accuracy |
|---|---|---|
| High | 12 | 100% |
| Medium | 18 | 67% |

**semantic**

| Label | n | Top-1 accuracy |
|---|---|---|
| High | 24 | 100% |
| Medium | 12 | 67% |

## Spotlight

**Spotlight — "Can I WFH?":** semantic retrieval ranks the remote work policy #1 at 0.315 (Medium); TF-IDF scored 0.000 against an unrelated entry and fell to a coverage gap.

## Answer quality (Claude-as-judge, semantic retriever)

- Cases judged: 32
- Grounded in sources: 100%
- Cites a source: 100%

## Per-case results

**tfidf**

| id | type | rank | top-1 score | label | top-1 match |
|---|---|---|---|---|---|
| V1 | verbatim | 1 | 0.683 | High | Where can I find the latest pricing guidance? |
| V2 | verbatim | 1 | 0.611 | High | What is the remote work policy? |
| V3 | verbatim | 1 | 0.569 | High | How do I request vendor approval? |
| V4 | verbatim | 1 | 0.558 | High | How do I issue a refund to a customer? |
| V5 | verbatim | 1 | 0.501 | High | What are the password requirements? |
| V6 | verbatim | 1 | 0.550 | High | How do I submit an expense report? |
| V7 | verbatim | 1 | 0.492 | High | What is the data retention policy? |
| V8 | verbatim | 1 | 0.558 | High | When do my benefits start? |
| V9 | verbatim | 1 | 0.574 | High | How do I set up VPN access? |
| P1 | paraphrase | 1 | 0.190 | Medium | Can I offer a discount to close a deal? |
| P2 | paraphrase | 1 | 0.294 | Medium | Can I share our product roadmap with a prospect? |
| P3 | paraphrase | 1 | 0.632 | High | How much paid time off do I get per year? |
| P4 | paraphrase | 1 | 0.486 | High | When are performance reviews held? |
| P5 | paraphrase | 1 | 0.402 | Medium | What is the process for booking business travel? |
| P6 | paraphrase | 1 | 0.220 | Medium | How do I reserve a conference room? |
| P7 | paraphrase | 1 | 0.410 | Medium | What is the SLA for responding to support ticket |
| P8 | paraphrase | 1 | 0.395 | Medium | How do I escalate an outage reported by a custom |
| P9 | paraphrase | 1 | 0.591 | High | Can I upload customer data into an AI tool? |
| P10 | paraphrase | 1 | 0.208 | Medium | What is the corporate card policy? |
| P11 | paraphrase | 1 | 0.429 | Medium | Can I sign a contract on behalf of the company? |
| P12 | paraphrase | 1 | 0.407 | Medium | How do I get access to internal systems as a new |
| P13 | paraphrase | 2 | 0.345 | Medium | Can I install unapproved software on my work lap |
| K1 | keyword_mismatch | — | 0.000 | gap | How do I set up VPN access? |
| K2 | keyword_mismatch | 1 | 0.329 | Medium | What is the parental leave policy? |
| K3 | keyword_mismatch | 1 | 0.372 | Medium | What should I do if I clicked a phishing link? |
| K4 | keyword_mismatch | — | 0.144 | gap | How do I set up VPN access? |
| K5 | keyword_mismatch | 1 | 0.136 | gap | How much paid time off do I get per year? |
| K6 | keyword_mismatch | — | 0.304 | Medium | What is the remote work policy? |
| K7 | keyword_mismatch | 1 | 0.205 | Medium | How do I issue a refund to a customer? |
| K8 | keyword_mismatch | 1 | 0.155 | gap | Do I need an NDA before sharing confidential inf |
| K9 | keyword_mismatch | — | 0.000 | gap | How do I set up VPN access? |
| K10 | keyword_mismatch | 1 | 0.138 | gap | Where do I find approved customer case studies? |
| O1 | off_kb | n/a | 0.144 | gap | How do I set up VPN access? |
| O2 | off_kb | n/a | 0.000 | gap | How do I set up VPN access? |
| O3 | off_kb | n/a | 0.172 | Medium | What are the password requirements? |
| O4 | off_kb | n/a | 0.304 | Medium | What is the remote work policy? |
| O5 | off_kb | n/a | 0.151 | gap | What is the corporate card policy? |
| O6 | off_kb | n/a | 0.165 | Medium | Can I sign a contract on behalf of the company? |
| O7 | off_kb | n/a | 0.310 | Medium | What are the password requirements? |
| O8 | off_kb | n/a | 0.154 | gap | How do I issue a refund to a customer? |

**semantic**

| id | type | rank | top-1 score | label | top-1 match |
|---|---|---|---|---|---|
| V1 | verbatim | 1 | 0.853 | High | Where can I find the latest pricing guidance? |
| V2 | verbatim | 1 | 0.766 | High | What is the remote work policy? |
| V3 | verbatim | 1 | 0.905 | High | How do I request vendor approval? |
| V4 | verbatim | 1 | 0.864 | High | How do I issue a refund to a customer? |
| V5 | verbatim | 1 | 0.891 | High | What are the password requirements? |
| V6 | verbatim | 1 | 0.862 | High | How do I submit an expense report? |
| V7 | verbatim | 1 | 0.800 | High | What is the data retention policy? |
| V8 | verbatim | 1 | 0.800 | High | When do my benefits start? |
| V9 | verbatim | 1 | 0.848 | High | How do I set up VPN access? |
| P1 | paraphrase | 1 | 0.616 | High | Can I offer a discount to close a deal? |
| P2 | paraphrase | 1 | 0.631 | High | Can I share our product roadmap with a prospect? |
| P3 | paraphrase | 1 | 0.726 | High | How much paid time off do I get per year? |
| P4 | paraphrase | 1 | 0.679 | High | When are performance reviews held? |
| P5 | paraphrase | 1 | 0.727 | High | What is the process for booking business travel? |
| P6 | paraphrase | 1 | 0.605 | High | How do I reserve a conference room? |
| P7 | paraphrase | 1 | 0.694 | High | What is the SLA for responding to support ticket |
| P8 | paraphrase | 1 | 0.780 | High | How do I escalate an outage reported by a custom |
| P9 | paraphrase | 1 | 0.782 | High | Can I upload customer data into an AI tool? |
| P10 | paraphrase | 1 | 0.662 | High | What is the corporate card policy? |
| P11 | paraphrase | 1 | 0.817 | High | Can I sign a contract on behalf of the company? |
| P12 | paraphrase | 1 | 0.725 | High | How do I get access to internal systems as a new |
| P13 | paraphrase | 1 | 0.617 | High | How do I request a new laptop or hardware? |
| K1 | keyword_mismatch | 1 | 0.315 | Medium | What is the remote work policy? |
| K2 | keyword_mismatch | 1 | 0.480 | Medium | What is the parental leave policy? |
| K3 | keyword_mismatch | 1 | 0.484 | Medium | What should I do if I clicked a phishing link? |
| K4 | keyword_mismatch | 1 | 0.389 | Medium | Can I upload customer data into an AI tool? |
| K5 | keyword_mismatch | 1 | 0.747 | High | How much paid time off do I get per year? |
| K6 | keyword_mismatch | 1 | 0.464 | Medium | How do I report a workplace concern or harassmen |
| K7 | keyword_mismatch | 1 | 0.545 | Medium | How do I issue a refund to a customer? |
| K8 | keyword_mismatch | 1 | 0.611 | High | Do I need an NDA before sharing confidential inf |
| K9 | keyword_mismatch | 1 | 0.353 | Medium | What is the purchasing approval threshold? |
| K10 | keyword_mismatch | 1 | 0.450 | Medium | Where do I find approved customer case studies? |
| O1 | off_kb | n/a | 0.207 | gap | Can I install unapproved software on my work lap |
| O2 | off_kb | n/a | 0.109 | gap | How do I escalate an outage reported by a custom |
| O3 | off_kb | n/a | 0.514 | Medium | What are the password requirements? |
| O4 | off_kb | n/a | 0.264 | gap | How do I request a new laptop or hardware? |
| O5 | off_kb | n/a | 0.387 | Medium | How do I submit an expense report? |
| O6 | off_kb | n/a | 0.405 | Medium | Where can I find the latest pricing guidance? |
| O7 | off_kb | n/a | 0.482 | Medium | What are the password requirements? |
| O8 | off_kb | n/a | 0.266 | gap | What should I do if I clicked a phishing link? |
