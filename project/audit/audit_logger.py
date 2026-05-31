"""Audit logging for the trustworthiness-enhanced RAG advisory system.

Provides append-only JSONL logging of each query interaction, capturing:
- timestamp
- query text
- sources cited (filenames)
- per-source tier metadata
- low_confidence flag
- max retrieval grade (if available)

Design: JSONL was chosen over SQLite for proof-of-concept simplicity —
append-only, no schema migration, no lock contention. Production
deployments should migrate to a queryable database (e.g. PostgreSQL
with JSONB) for query/analytics capability and retention policies.
"""

import os
import json
import re
from datetime import datetime
from typing import List, Optional

# Log location relative to project root (assumes cwd when called)
AUDIT_LOG_DIR = "evaluation/audit"
AUDIT_LOG_FILE = os.path.join(AUDIT_LOG_DIR, "queries.jsonl")


def _ensure_log_dir():
    """Create audit log directory if it doesn't exist."""
    os.makedirs(AUDIT_LOG_DIR, exist_ok=True)


def _extract_sources_from_text(text: str) -> List[str]:
    """Extract markdown filenames from final answer text via regex."""
    return sorted(set(re.findall(r"\b([\w\-]+\.md)\b", text)))


def log_query(
    query: str,
    answer_text: str,
    sub_answers: list,
    sources_metadata: Optional[dict] = None,
) -> bool:
    """Append one audit record for a completed query.

    Args:
        query: The original user query.
        answer_text: The final aggregated answer (including trust footer).
        sub_answers: List of agent sub-answer dicts (each has 'low_confidence').
        sources_metadata: Optional dict mapping filename → metadata dict
                          (tier, source_type, primary_url, last_retrieved).
                          If None, only filenames are logged.

    Returns:
        True if logging succeeded, False otherwise. Failures are silent
        (no exception raised) to avoid breaking the user-facing flow.
    """
    try:
        _ensure_log_dir()

        sources = _extract_sources_from_text(answer_text)
        any_low_conf = any(a.get("low_confidence", False) for a in sub_answers)

        record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "query": query,
            "sources": sources,
            "sources_metadata": sources_metadata or {},
            "low_confidence": any_low_conf,
            "num_sub_answers": len(sub_answers),
            "answer_length_chars": len(answer_text),
        }

        with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

        return True
    except Exception as e:
        # Silent failure — audit logging must not break user experience
        # In production, this would emit a metric / alert instead of printing
        print(f"[audit_logger] WARNING: log_query failed: {e}")
        return False


def read_audit_log(limit: Optional[int] = None) -> List[dict]:
    """Read audit log entries (most recent first if limit specified).

    Used by Phase E evaluation scripts to compute aggregate statistics.
    """
    if not os.path.isfile(AUDIT_LOG_FILE):
        return []

    records = []
    with open(AUDIT_LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    if limit is not None:
        records = records[-limit:]

    return records
