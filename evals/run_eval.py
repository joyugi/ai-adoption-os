"""Golden-set evaluation harness for AI Adoption OS retrieval.

Usage:
    python evals/run_eval.py --retriever both
    python evals/run_eval.py --retriever semantic --tune-thresholds
    python evals/run_eval.py --retriever both --judge --out evals/results/eval_report.md
"""

import argparse
import csv
import sys
from datetime import date
from pathlib import Path

import numpy as np

EVALS_DIR = Path(__file__).parent
ROOT = EVALS_DIR.parent
sys.path.insert(0, str(ROOT / "prototype"))

import retrieval_semantic
import retrieval_tfidf

GOLDEN_PATH = EVALS_DIR / "golden_set.csv"
TOP_K = 3
CASE_TYPES = ["verbatim", "paraphrase", "keyword_mismatch"]


def load_golden() -> list[dict]:
    with open(GOLDEN_PATH, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def run_retriever(engine, cases: list[dict]) -> list[dict]:
    results = []
    for case in cases:
        ranked = engine.search(case["query"], top_k=TOP_K)
        top_score = ranked[0][1]
        rank = None
        if case["expected_question"]:
            for i, (row, _score) in enumerate(ranked, start=1):
                if row["question"] == case["expected_question"]:
                    rank = i
                    break
        results.append({
            "id": case["id"],
            "case_type": case["case_type"],
            "query": case["query"],
            "expected": case["expected_question"],
            "answerable": bool(case["expected_question"]),
            "top1_question": ranked[0][0]["question"],
            "top1_score": top_score,
            "rank": rank,
            "label": engine.confidence_label(top_score),
        })
    return results


def summarize(results: list[dict]) -> dict:
    answerable = [r for r in results if r["answerable"]]
    off_kb = [r for r in results if not r["answerable"]]

    def hit_at(rs, k):
        return sum(1 for r in rs if r["rank"] is not None and r["rank"] <= k) / len(rs)

    by_type = {}
    for ct in CASE_TYPES:
        rs = [r for r in answerable if r["case_type"] == ct]
        by_type[ct] = {"n": len(rs), "hit1": hit_at(rs, 1), "hit3": hit_at(rs, 3)}

    calibration = {}
    for label in ["High", "Medium"]:
        rs = [r for r in results if r["label"] == label]
        correct = sum(1 for r in rs if r["answerable"] and r["rank"] == 1)
        calibration[label] = {"n": len(rs), "accuracy": correct / len(rs) if rs else None}

    return {
        "n_answerable": len(answerable),
        "n_off_kb": len(off_kb),
        "hit1": hit_at(answerable, 1),
        "hit3": hit_at(answerable, 3),
        "mrr": float(np.mean([1 / r["rank"] if r["rank"] else 0.0 for r in answerable])),
        "correct_refusal": sum(1 for r in off_kb if r["label"] is None) / len(off_kb),
        "false_refusal": sum(1 for r in answerable if r["label"] is None) / len(answerable),
        "by_type": by_type,
        "calibration": calibration,
    }


def balanced_accuracy(results: list[dict], t: float) -> float:
    answerable = [r for r in results if r["answerable"]]
    off_kb = [r for r in results if not r["answerable"]]
    answered_ok = sum(1 for r in answerable if r["top1_score"] >= t and r["rank"] == 1)
    refused_ok = sum(1 for r in off_kb if r["top1_score"] < t)
    return (answered_ok / len(answerable) + refused_ok / len(off_kb)) / 2


def tune_thresholds(results: list[dict]) -> dict:
    scores = [r["top1_score"] for r in results]
    grid = np.arange(0.0, max(scores) + 0.005, 0.005)

    # MEDIUM: maximize balanced accuracy; tie-break toward higher t
    # (prefer escalation over a wrong answer)
    best_t, best_ba = 0.0, -1.0
    for t in grid:
        ba = balanced_accuracy(results, t)
        if ba >= best_ba:
            best_ba, best_t = ba, t
    medium = float(best_t)

    # HIGH: smallest t where every case scoring >= t is answerable with a
    # correct top-1 hit at >= 95% precision
    high = None
    for t in grid:
        if t <= medium:
            continue
        qualifying = [r for r in results if r["top1_score"] >= t]
        if not qualifying:
            break
        precision = sum(
            1 for r in qualifying if r["answerable"] and r["rank"] == 1
        ) / len(qualifying)
        if precision >= 0.95:
            high = float(t)
            break
    if high is None:
        high = float(max(scores))

    sensitivity = {
        round(medium + d, 3): round(balanced_accuracy(results, medium + d), 3)
        for d in (-0.05, -0.025, 0.0, 0.025, 0.05)
        if medium + d >= 0
    }
    return {
        "medium": round(medium, 3),
        "high": round(high, 3),
        "balanced_accuracy": round(best_ba, 3),
        "sensitivity": sensitivity,
    }


def pct(x: float) -> str:
    return f"{100 * x:.0f}%"


def render_report(all_results: dict[str, list[dict]],
                  all_summaries: dict[str, dict],
                  judge_summary: dict | None) -> str:
    lines = [
        "# Retrieval Evaluation Report",
        "",
        f"- Date: {date.today().isoformat()}",
        f"- Golden set: {GOLDEN_PATH.name} "
        f"({sum(1 for _ in load_golden())} cases: 32 answerable, 8 off-KB)",
        f"- Embedding model: {retrieval_semantic.MODEL_NAME}",
        f"- Thresholds — TF-IDF: High ≥{retrieval_tfidf.HIGH_CONFIDENCE_THRESHOLD}, "
        f"Medium ≥{retrieval_tfidf.MEDIUM_CONFIDENCE_THRESHOLD}; "
        f"Semantic: High ≥{retrieval_semantic.HIGH_CONFIDENCE_THRESHOLD}, "
        f"Medium ≥{retrieval_semantic.MEDIUM_CONFIDENCE_THRESHOLD}",
        "",
        "## Overall comparison",
        "",
        "| Metric | " + " | ".join(all_summaries) + " |",
        "|---|" + "---|" * len(all_summaries),
    ]
    rows = [
        ("Hit@1 (32 answerable)", lambda s: pct(s["hit1"])),
        ("Hit@3", lambda s: pct(s["hit3"])),
        ("MRR", lambda s: f"{s['mrr']:.2f}"),
        ("Correct refusal (8 off-KB)", lambda s: pct(s["correct_refusal"])),
        ("False refusal (answerable)", lambda s: pct(s["false_refusal"])),
    ]
    for name, fn in rows:
        lines.append(f"| {name} | " + " | ".join(fn(s) for s in all_summaries.values()) + " |")

    lines += ["", "## Hit@1 by case type", "",
              "| Case type | n | " + " | ".join(all_summaries) + " |",
              "|---|---|" + "---|" * len(all_summaries)]
    for ct in CASE_TYPES:
        n = next(iter(all_summaries.values()))["by_type"][ct]["n"]
        cells = " | ".join(pct(s["by_type"][ct]["hit1"]) for s in all_summaries.values())
        lines.append(f"| {ct} | {n} | {cells} |")

    lines += ["", "## Confidence calibration (top-1 accuracy per label)", ""]
    for name, summary in all_summaries.items():
        lines.append(f"**{name}**")
        lines.append("")
        lines.append("| Label | n | Top-1 accuracy |")
        lines.append("|---|---|---|")
        for label, cal in summary["calibration"].items():
            acc = pct(cal["accuracy"]) if cal["accuracy"] is not None else "—"
            lines.append(f"| {label} | {cal['n']} | {acc} |")
        lines.append("")

    if "semantic" in all_results:
        wfh = next(r for r in all_results["semantic"] if r["id"] == "K1")
        spotlight = (f"**Spotlight — \"Can I WFH?\":** semantic retrieval ranks the remote "
                     f"work policy #{wfh['rank']} at {wfh['top1_score']:.3f} "
                     f"({wfh['label'] or 'coverage gap'})")
        if "tfidf" in all_results:
            wfh_t = next(r for r in all_results["tfidf"] if r["id"] == "K1")
            spotlight += (f"; TF-IDF scored {wfh_t['top1_score']:.3f} against an unrelated "
                          f"entry and fell to a coverage gap")
        lines += ["## Spotlight", "", spotlight + ".", ""]

    if judge_summary:
        lines += ["## Answer quality (Claude-as-judge, semantic retriever)", "",
                  f"- Cases judged: {judge_summary['n']}",
                  f"- Grounded in sources: {pct(judge_summary['grounded_rate'])}",
                  f"- Cites a source: {pct(judge_summary['cited_rate'])}"]
        if judge_summary.get("issues"):
            lines += ["", "Issues flagged:"]
            lines += [f"- {case_id}: {issue}" for case_id, issue in judge_summary["issues"]]
        lines.append("")

    lines += ["## Per-case results", ""]
    for name, results in all_results.items():
        lines += [f"**{name}**", "",
                  "| id | type | rank | top-1 score | label | top-1 match |",
                  "|---|---|---|---|---|---|"]
        for r in results:
            rank = r["rank"] if r["rank"] else ("—" if r["answerable"] else "n/a")
            lines.append(f"| {r['id']} | {r['case_type']} | {rank} | "
                         f"{r['top1_score']:.3f} | {r['label'] or 'gap'} | "
                         f"{r['top1_question'][:48]} |")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--retriever", choices=["both", "tfidf", "semantic"], default="both")
    parser.add_argument("--tune-thresholds", action="store_true")
    parser.add_argument("--judge", action="store_true",
                        help="Score answer groundedness with Claude (requires API key)")
    parser.add_argument("--out", type=Path, help="Write markdown report to this path")
    args = parser.parse_args()

    engines = {"tfidf": retrieval_tfidf, "semantic": retrieval_semantic}
    if args.retriever != "both":
        engines = {args.retriever: engines[args.retriever]}

    cases = load_golden()
    all_results = {name: run_retriever(engine, cases) for name, engine in engines.items()}
    all_summaries = {name: summarize(results) for name, results in all_results.items()}

    for name, s in all_summaries.items():
        print(f"\n=== {name} ===")
        print(f"hit@1 {pct(s['hit1'])} | hit@3 {pct(s['hit3'])} | MRR {s['mrr']:.2f} | "
              f"correct refusal {pct(s['correct_refusal'])} | "
              f"false refusal {pct(s['false_refusal'])}")
        for ct, m in s["by_type"].items():
            print(f"  {ct} (n={m['n']}): hit@1 {pct(m['hit1'])}, hit@3 {pct(m['hit3'])}")

    if args.tune_thresholds:
        for name, results in all_results.items():
            tuned = tune_thresholds(results)
            print(f"\n=== tuned thresholds ({name}) ===")
            print(f"MEDIUM = {tuned['medium']} (balanced accuracy {tuned['balanced_accuracy']})")
            print(f"HIGH   = {tuned['high']}")
            print(f"sensitivity around MEDIUM: {tuned['sensitivity']}")

    judge_summary = None
    if args.judge:
        from judge import run_judge
        target = all_results.get("semantic")
        if target is None:
            print("\n--judge requires the semantic retriever; skipping.")
        else:
            judge_summary = run_judge(target)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(render_report(all_results, all_summaries, judge_summary),
                            encoding="utf-8")
        print(f"\nReport written to {args.out}")


if __name__ == "__main__":
    main()
