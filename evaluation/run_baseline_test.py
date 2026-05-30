"""
Run baseline test questions against the RAG system and save results.

Usage:
    python run_baseline_test.py                              # English questions, baseline_results_en.md
    python run_baseline_test.py --lang zh                    # Chinese questions, baseline_results_zh.md
    python run_baseline_test.py --output custom_name.md      # English questions, custom filename
    python run_baseline_test.py --lang en --output baseline_results_v2_english_docs_en.md
"""

import argparse
import os
import re
import sys
from datetime import datetime

# Add project/ to path so we can import project modules directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "project"))

from core.rag_system import RAGSystem
from core.document_manager import DocumentManager
from core.chat_interface import ChatInterface

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

QUESTIONS_FILE = os.path.join(os.path.dirname(__file__), "test_questions.md")
KNOWLEDGE_BASE = "Curated markdown knowledge base (UTS_Master_of_IT.md, UNSW_Master_of_IT.md)"

# ---------------------------------------------------------------------------
# Question loader
# ---------------------------------------------------------------------------

def load_questions(filepath, lang="en"):
    """
    Parse bilingual test_questions.md.
    Returns list of (label, question_text) e.g. [("Q1", "As an international..."), ("Q11a", "...")]
    lang: "en" -> extract **EN:** lines; "zh" -> extract **ZH:** lines
    """
    pattern_heading = re.compile(r"^### (Q\d+[ab]?)$", re.MULTILINE)
    pattern_en = re.compile(r"^\*\*EN:\*\*\s*(.+)$", re.MULTILINE)
    pattern_zh = re.compile(r"^\*\*ZH:\*\*\s*(.+)$", re.MULTILINE)

    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    headings = [(m.group(1), m.start()) for m in pattern_heading.finditer(content)]
    results = []
    for i, (label, start) in enumerate(headings):
        end = headings[i + 1][1] if i + 1 < len(headings) else len(content)
        block = content[start:end]
        pattern = pattern_zh if lang == "zh" else pattern_en
        m = pattern.search(block)
        if m:
            results.append((label, m.group(1).strip()))

    return results

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run_question(chat_interface, rag_system, question, clarification_reply):
    """Run a single question through the RAG pipeline and return (answer, sources, clarification_triggered)."""
    rag_system.reset_thread()

    final_messages = []
    for msgs in chat_interface.chat(question, []):
        final_messages = msgs

    # Detect clarification interrupt
    has_clarification = any(
        m.get("metadata", {}).get("node") == "clarification"
        for m in final_messages
    )

    if has_clarification:
        print("    [clarification triggered — sending follow-up]")
        for msgs in chat_interface.chat(clarification_reply, []):
            final_messages = msgs

    # Extract plain answer (messages with no metadata = final LLM output)
    answer_parts = [
        m["content"]
        for m in final_messages
        if m.get("role") == "assistant" and "metadata" not in m
    ]
    answer = "\n".join(answer_parts).strip() or "（系統未產生回答）"

    # Extract source filenames from tool result messages
    sources = set()
    for m in final_messages:
        if "metadata" in m:
            content = m.get("content", "")
            found = re.findall(r"[\w]+(?:_[\w]+)*\.(?:pdf|md)", content)
            sources.update(found)

    return answer, sorted(sources), has_clarification


def format_result(label, question, answer, sources, clarification_triggered, timestamp):
    source_str = ", ".join(sources) if sources else "(none detected)"
    clarification_note = "\n> ⚠️ System triggered clarification; auto-replied to continue with available information.\n" if clarification_triggered else ""
    return f"""## {label}: {question}
{clarification_note}
**Timestamp:** {timestamp}
**Knowledge Base:** {KNOWLEDGE_BASE}

**System Response:**
{answer}

**Sources:** {source_str}

**Initial Assessment:**
- Correctness: Pending manual review
- Source Attribution: Pending manual review
- Uncertainty Signaling: Pending manual review

---
"""

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Run baseline RAG evaluation test.")
    parser.add_argument("--lang", choices=["en", "zh"], default="en",
                        help="Question language to run (default: en)")
    parser.add_argument("--output", default=None,
                        help="Output filename (default: baseline_results_{lang}.md)")
    args = parser.parse_args()

    output_filename = args.output or f"baseline_results_{args.lang}.md"
    output_path = os.path.join(os.path.dirname(__file__), "baseline", output_filename)
    clarification_reply = (
        "Please answer using the available information without further clarification."
        if args.lang == "en"
        else "請直接用現有資訊回答，不需要澄清。"
    )

    print("\n=== Baseline Test ===")
    print(f"Language: {args.lang} | Output: {output_filename}")
    print("Initializing RAG system...")

    rag_system = RAGSystem()
    rag_system.initialize()

    doc_manager = DocumentManager(rag_system)
    doc_manager.ingest_existing_markdowns()

    chat_interface = ChatInterface(rag_system)

    questions = load_questions(QUESTIONS_FILE, lang=args.lang)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    header = f"""# Baseline Test Results

**測試時間：** {timestamp}
**知識庫：** {KNOWLEDGE_BASE}
**模型：** 依 config.py 設定（預設 Ollama 本地模型）
**語言：** {args.lang.upper()}

---

"""

    results = [header]

    for i, (label, question) in enumerate(questions, start=1):
        print(f"\n[{i}/{len(questions)}] [{label}] {question[:60]}...")
        answer, sources, clarification_triggered = run_question(chat_interface, rag_system, question, clarification_reply)
        result_block = format_result(label, question, answer, sources, clarification_triggered, timestamp)
        results.append(result_block)
        print(f"    → done. sources: {sources or '(none)'}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(results)

    print(f"\n測試完成，共 {len(questions)} 題，結果已存入 {output_path}")


if __name__ == "__main__":
    main()
