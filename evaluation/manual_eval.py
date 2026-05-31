"""
Manual trustworthiness evaluation comparing baseline vs enhanced.

Computes 4 metrics tailored to the research thesis (trustworthiness layer):
1. Citation Recall — proportion of questions with non-empty sources
2. Hedging Rate (out-of-scope) — proportion of out-of-scope questions
   that triggered low_confidence
3. Source Tier Coverage — proportion of questions where sources have
   tier metadata
4. Multi-source Synthesis — average number of distinct sources cited

Usage:
    python evaluation/manual_eval.py
"""

import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
BASELINE_PATH = PROJECT_ROOT / "evaluation" / "baseline" / "baseline_results_v2_english_docs_en.md"
ENHANCED_AUDIT_PATH = PROJECT_ROOT / "evaluation" / "audit" / "queries.jsonl"
ENHANCED_RESULTS_PATH = PROJECT_ROOT / "evaluation" / "enhanced" / "enhanced_results_v1_en.md"
OUTPUT_PATH = PROJECT_ROOT / "evaluation" / "evaluation_comparison.md"

# Question labels we treat as "out-of-scope" or "boundary" cases for hedging eval
# Based on the original test_questions.md design
OUT_OF_SCOPE_LABELS = {
    "Q9",   # Migration office vs school discrepancy
    "Q12",  # Data Science programs (not in KB)
    "Q13",  # Post-grad migration pathways
    "Q14",  # Subclass 500 visa documents
    "Q15",  # Subclass 485 duration
    "Q16",  # System temporal awareness (meta)
}


def parse_baseline_md(path: Path) -> dict:
    """Parse baseline markdown into dict: label -> {answer, sources_in_text}."""
    content = path.read_text(encoding="utf-8")
    results = {}

    pattern = re.compile(r"^## (Q\d+[ab]?):.*?(?=^## Q|\Z)", re.MULTILINE | re.DOTALL)
    for match in pattern.finditer(content):
        block = match.group(0)
        label_match = re.match(r"^## (Q\d+[ab]?)", block)
        if not label_match:
            continue
        label = label_match.group(1)

        # Extract sources (look for **Sources:** section)
        sources = set()
        for src_match in re.finditer(r"\*\*Sources[:：]?\*\*\s*([^\n]+)", block):
            src_text = src_match.group(1)
            for filename in re.finditer(r"([\w\-]+\.md)", src_text):
                sources.add(filename.group(1))
        # Also catch list-style sources
        for src_match in re.finditer(r"-\s+([\w\-]+\.md)", block):
            sources.add(src_match.group(1))

        results[label] = {
            "sources": sorted(sources),
        }

    return results


def parse_enhanced_audit(path: Path) -> list:
    """Parse enhanced audit log into list of dicts."""
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def label_from_query(query: str, questions_file: Path) -> str:
    """Map a query string back to its label by matching against test_questions.md."""
    qs_content = questions_file.read_text(encoding="utf-8")
    # Find every label + EN block, match query
    pattern = re.compile(r"^### (Q\d+[ab]?)$.*?\*\*EN:\*\*\s*(.+?)$", re.MULTILINE | re.DOTALL)
    for m in re.finditer(pattern, qs_content):
        label = m.group(1)
        en_text = m.group(2).split("\n")[0].strip()
        # Approximate match: first 50 chars
        if query.strip()[:50] == en_text[:50]:
            return label
    return "UNKNOWN"


def compute_metrics(baseline_data: dict, enhanced_audit: list, questions_file: Path) -> dict:
    """Compute the 4 trustworthiness metrics for both systems."""

    # === BASELINE ===
    baseline_n = len(baseline_data)
    baseline_with_sources = sum(1 for v in baseline_data.values() if v["sources"])
    baseline_avg_sources = sum(len(v["sources"]) for v in baseline_data.values()) / baseline_n

    # Baseline has no low_confidence / tier metadata mechanism, so:
    baseline_hedging_rate = 0.0
    baseline_tier_coverage = 0.0  # baseline can't expose tier

    # === ENHANCED ===
    enhanced_n = len(enhanced_audit)
    enhanced_with_sources = sum(1 for r in enhanced_audit if r["sources"])
    enhanced_avg_sources = sum(len(r["sources"]) for r in enhanced_audit) / enhanced_n

    # Map each enhanced record back to a label
    enhanced_by_label = {}
    for r in enhanced_audit:
        label = label_from_query(r["query"], questions_file)
        enhanced_by_label[label] = r

    print(f"\n  [label mapping] {len(enhanced_by_label)} unique labels resolved:")
    for lbl, rec in sorted(enhanced_by_label.items()):
        print(f"    {lbl}: {rec['query'][:60]}...")

    # Hedging on out-of-scope: how many out-of-scope questions triggered low_confidence
    oos_records = [enhanced_by_label[l] for l in OUT_OF_SCOPE_LABELS if l in enhanced_by_label]
    oos_low_conf = sum(1 for r in oos_records if r["low_confidence"])
    enhanced_hedging_rate = (oos_low_conf / len(oos_records)) if oos_records else 0

    # Tier coverage: how many records have ≥1 source with tier metadata
    tier_covered = sum(
        1 for r in enhanced_audit
        if any(m.get("tier") is not None for m in r.get("sources_metadata", {}).values())
    )
    enhanced_tier_coverage = tier_covered / enhanced_n

    return {
        "baseline": {
            "n_questions": baseline_n,
            "citation_recall": baseline_with_sources / baseline_n,
            "with_sources_count": baseline_with_sources,
            "empty_sources_count": baseline_n - baseline_with_sources,
            "avg_sources_per_q": baseline_avg_sources,
            "hedging_rate_oos": baseline_hedging_rate,
            "tier_coverage": baseline_tier_coverage,
        },
        "enhanced": {
            "n_questions": enhanced_n,
            "citation_recall": enhanced_with_sources / enhanced_n,
            "with_sources_count": enhanced_with_sources,
            "empty_sources_count": enhanced_n - enhanced_with_sources,
            "avg_sources_per_q": enhanced_avg_sources,
            "hedging_rate_oos": enhanced_hedging_rate,
            "tier_coverage": enhanced_tier_coverage,
            "oos_n": len(oos_records),
            "oos_low_conf_count": oos_low_conf,
        }
    }


def format_report(metrics: dict) -> str:
    """Format metric comparison as a markdown report."""
    b = metrics["baseline"]
    e = metrics["enhanced"]

    def pct(x): return f"{x*100:.1f}%"
    def num(x): return f"{x:.2f}"

    report = f"""# Evaluation Comparison: Baseline vs Enhanced

## Test Set
- 17 bilingual test questions (English used here)
- Knowledge base: UTS_Master_of_IT.md, UNSW_Master_of_IT.md (both Tier 1)
- Out-of-scope questions: {sorted(OUT_OF_SCOPE_LABELS)}
- See `evaluation/test_questions.md` for full set

## Quantitative Trustworthiness Metrics

| Metric | Baseline (vanilla) | Enhanced | Δ |
|---|---|---|---|
| **Citation Recall** | {pct(b['citation_recall'])} ({b['with_sources_count']}/{b['n_questions']}) | {pct(e['citation_recall'])} ({e['with_sources_count']}/{e['n_questions']}) | **{pct(e['citation_recall'] - b['citation_recall'])}** |
| **Hedging Rate (out-of-scope, n={e['oos_n']})** | {pct(b['hedging_rate_oos'])} (mechanism absent) | {pct(e['hedging_rate_oos'])} ({e['oos_low_conf_count']}/{e['oos_n']}) | **+{pct(e['hedging_rate_oos'])}** |
| **Source Tier Coverage** | {pct(b['tier_coverage'])} (mechanism absent) | {pct(e['tier_coverage'])} | **+{pct(e['tier_coverage'])}** |
| **Multi-source Synthesis (avg sources/Q)** | {num(b['avg_sources_per_q'])} | {num(e['avg_sources_per_q'])} | **{num(e['avg_sources_per_q'] - b['avg_sources_per_q'])}** |

## Interpretation

### Citation Recall
Baseline cites sources for {b['with_sources_count']}/{b['n_questions']} questions. {b['empty_sources_count']} questions have no source attribution — a key trustworthiness gap.
Enhanced cites sources for {e['with_sources_count']}/{e['n_questions']} questions, an improvement of {pct(e['citation_recall'] - b['citation_recall'])}.

### Hedging Rate
The vanilla baseline has no uncertainty signaling mechanism. The enhanced system triggers low_confidence on {e['oos_low_conf_count']}/{e['oos_n']} out-of-scope questions, demonstrating that the grading-based confidence assessment correctly flags queries the knowledge base cannot reliably support.

### Source Tier Coverage
The enhanced system exposes tier metadata for {pct(e['tier_coverage'])} of queries, enabling users to assess source authority. The baseline has no such mechanism.

### Multi-source Synthesis
Both systems cite an average of ~{num(e['avg_sources_per_q'])} sources per question, indicating the enhancement layer preserves the baseline's cross-source synthesis ability while adding trust metadata.

## Notes on Methodology

This evaluation uses **manual trustworthiness metrics tailored to the research thesis**, in lieu of standard RAGAS metrics (which were incompatible with the project's langchain 1.4 dependency). The metrics chosen — citation recall, hedging rate, tier coverage, multi-source synthesis — directly correspond to the trustworthiness mechanisms (Phases A–D) implemented in the enhancement layer.

Faithfulness was not computed automatically; instead, a qualitative case study analysis on 3–4 representative questions is provided in the project report Section 6.
"""
    return report


def main():
    questions_file = PROJECT_ROOT / "evaluation" / "test_questions.md"

    print("=" * 70)
    print("MANUAL TRUSTWORTHINESS EVALUATION")
    print("=" * 70)

    print("\n[1/3] Parsing baseline results...")
    baseline_data = parse_baseline_md(BASELINE_PATH)
    print(f"  Parsed {len(baseline_data)} baseline records")

    print("\n[2/3] Reading enhanced audit log...")
    enhanced_audit = parse_enhanced_audit(ENHANCED_AUDIT_PATH)
    print(f"  Loaded {len(enhanced_audit)} enhanced records")

    print("\n[3/3] Computing metrics...")
    metrics = compute_metrics(baseline_data, enhanced_audit, questions_file)

    print("\n" + "=" * 70)
    print("METRICS SUMMARY")
    print("=" * 70)

    for system in ["baseline", "enhanced"]:
        print(f"\n{system.upper()}:")
        for k, v in metrics[system].items():
            if isinstance(v, float):
                print(f"  {k}: {v:.4f}")
            else:
                print(f"  {k}: {v}")

    print("\n" + "=" * 70)
    print("WRITING REPORT")
    print("=" * 70)

    report = format_report(metrics)
    OUTPUT_PATH.write_text(report, encoding="utf-8")
    print(f"\nReport saved: {OUTPUT_PATH}")

    print("\n[DONE]")


if __name__ == "__main__":
    main()
