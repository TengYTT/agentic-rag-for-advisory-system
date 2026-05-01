import os
import sys
import re
from datetime import datetime

# Add project/ to path so we can import project modules directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "project"))

from core.rag_system import RAGSystem
from core.document_manager import DocumentManager
from core.chat_interface import ChatInterface

# ---------------------------------------------------------------------------
# Test questions
# ---------------------------------------------------------------------------

QUESTIONS = [
    "我是國際學生，大學讀商科（行銷）背景，想申請 UTS Master of IT，我符合入學資格嗎？",
    "非 IT 背景的學生申請 UNSW Master of IT，需要補修哪些先修課程？GPA 不到 3.0 的學生可以申請嗎？",
    "UTS MIT 和 UNSW MIT 有什麼差別？",
    "UTS MIT 和 UNSW MIT 的英文門檻需要幾分？如果我的英文程度比較一般的話，建議以哪一個為主要的申請目標？",
    "UTS MIT 和 UNSW MIT 國際學生的學費比較",
    "UTS MIT 和 UNSW MIT 課程是幾年制的？可以兼職就讀嗎？",
    "UNSW MIT 2026 年的申請截止日期是什麼時候？現在申請來得及嗎？最快現在可以申請的是哪一個入學時間？有沒有開條件式錄取？",
    "我看到不同地方說的英文門檻不一樣，UNSW MIT 官方要求到底是雅思 6.5 還是 6.0？對應 PTE 要考多少分？",
    "移民局和學校說的學生簽證要求有出入，以哪個為準？",
    "請比較 UTS 和 UNSW 的 Master of IT，列出課程方向、費用、入學門檻、申請截止日期、課程特色、學校優缺點等差異。",
]

KNOWLEDGE_BASE = "Markdown 文件（UTS_Master_of_IT.md, UNSW_Master_of_IT.md）"

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "baseline", "baseline_results.md")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run_question(chat_interface, rag_system, question):
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
        for msgs in chat_interface.chat("請直接用現有資訊回答，不需要澄清。", []):
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


def format_result(idx, question, answer, sources, clarification_triggered, timestamp):
    source_str = ", ".join(sources) if sources else "（未偵測到來源）"
    clarification_note = "\n> ⚠️ 系統要求澄清，已自動回覆「請直接用現有資訊回答」繼續。\n" if clarification_triggered else ""
    return f"""## Q{idx}：{question}
{clarification_note}
**測試時間：** {timestamp}
**知識庫狀態：** {KNOWLEDGE_BASE}

**系統回答：**
{answer}

**Sources：**
{source_str}

**初步評估：**
- 正確性：待人工確認
- 有無引用來源：待確認
- 有無不確定性提示：待確認

---
"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("\n=== Baseline Test ===")
    print("Initializing RAG system...")

    rag_system = RAGSystem()
    rag_system.initialize()

    doc_manager = DocumentManager(rag_system)
    doc_manager.ingest_existing_markdowns()

    chat_interface = ChatInterface(rag_system)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    header = f"""# Baseline Test Results

**測試時間：** {timestamp}
**知識庫：** {KNOWLEDGE_BASE}
**模型：** 依 config.py 設定（預設 Ollama 本地模型）

---

"""

    results = [header]

    for i, question in enumerate(QUESTIONS, start=1):
        print(f"\n[{i}/{len(QUESTIONS)}] {question[:60]}...")
        answer, sources, clarification_triggered = run_question(chat_interface, rag_system, question)
        result_block = format_result(i, question, answer, sources, clarification_triggered, timestamp)
        results.append(result_block)
        print(f"    → done. sources: {sources or '(none)'}")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.writelines(results)

    print(f"\n測試完成，共 {len(QUESTIONS)} 題，結果已存入 {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
