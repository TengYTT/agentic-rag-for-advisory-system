# Project Notes — Agentic RAG for Dummies

> 中英對照技術說明 | Bilingual Technical Reference

---

## 1. 專案架構概覽 | Project Architecture Overview

```
project/
├── app.py                      # 應用程式入口點 | Application entry point
├── config.py                   # 全域設定（模型、路徑、參數）| Global settings
├── document_chunker.py         # PDF/MD 文件切塊邏輯 | Document chunking logic
├── utils.py                    # 工具函式 | Utility functions
│
├── core/                       # 核心業務邏輯 | Core business logic
│   ├── rag_system.py           # RAG 系統主類別，組裝所有元件 | Main class, assembles all components
│   ├── chat_interface.py       # 處理串流輸出、UI 訊息格式 | Handles streaming & UI message formatting
│   ├── document_manager.py     # 文件新增、清除 | Document add/clear operations
│   └── observability.py        # Langfuse 可觀測性整合 | Langfuse observability integration
│
├── db/                         # 資料庫層 | Database layer
│   ├── vector_db_manager.py    # Qdrant 向量資料庫（Hybrid 搜尋）| Qdrant vector DB (hybrid search)
│   └── parent_store_manager.py # Parent chunk 的 JSON 檔案儲存 | JSON file store for parent chunks
│
├── rag_agent/                  # LangGraph Agent 核心 | LangGraph agent core
│   ├── graph.py                # 建構並編譯兩個 StateGraph | Builds & compiles two StateGraphs
│   ├── nodes.py                # 所有 graph nodes 的實作 | All node implementations
│   ├── edges.py                # 條件路由邏輯 | Conditional routing logic
│   ├── graph_state.py          # State 型別定義 | State type definitions
│   ├── prompts.py              # 所有 LLM 系統提示詞 | All LLM system prompts
│   ├── schemas.py              # Pydantic 結構化輸出 schema | Pydantic structured output schemas
│   └── tools.py                # LangChain 工具定義（搜尋、取回）| LangChain tool definitions
│
└── ui/
    ├── gradio_app.py           # Gradio UI 建構 | Gradio UI construction
    └── css.py                  # 自訂 CSS 樣式 | Custom CSS styles
```

---

## 2. LangGraph Graph 結構 | LangGraph Graph Structure

這個專案有**兩層巢狀的 StateGraph**：
The project uses **two nested StateGraphs**:

### 外層 Graph（主流程）| Outer Graph (main flow) — `State`

```
START
  │
  ▼
summarize_history       # 摘要對話歷史（>4則訊息才執行）
  │                     # Summarize conversation history (only if >4 messages)
  ▼
rewrite_query           # 分析問題：是否清楚？拆成幾個子問題？
  │                     # Analyze query: clear? split into sub-questions?
  ├──[不清楚 / unclear]──► request_clarification ──► (interrupt, 等使用者回覆)
  │                                                   (interrupt, await user reply)
  └──[清楚 / clear]────► agent (×N，每個子問題平行執行)
                         (×N, parallel Send for each sub-question)
  ▼
aggregate_answers       # 將所有子問題的答案合成為一個完整回答
  │                     # Synthesize all sub-answers into one final response
  ▼
END
```

### 內層 Agent Subgraph（每個子問題）| Inner Agent Subgraph (per sub-question) — `AgentState`

```
START
  │
  ▼
orchestrator            # 呼叫 LLM，決定下一步要用哪個工具
  │                     # Calls LLM, decides which tool to use next
  ├──[有 tool calls]──► tools (ToolNode)
  │                       │
  │                       ▼
  │                     should_compress_context   # token 超標？
  │                       │                       # tokens over threshold?
  │                       ├──[是/yes]──► compress_context ──► orchestrator
  │                       └──[否/no]──────────────────────► orchestrator
  │
  ├──[達到上限 / hit limit]──► fallback_response
  │                              │
  └──[無 tool calls]──► collect_answer ◄──────────┘
                           │
                           ▼
                          END
```

### Nodes 一覽 | Node Summary

| Node | 所屬 Graph | 功能 |
|------|-----------|------|
| `summarize_history` | 外層 | 壓縮對話歷史為摘要 / Compress history into summary |
| `rewrite_query` | 外層 | 分析並重寫問題 / Analyze & rewrite query |
| `request_clarification` | 外層 | 中斷點，等使用者澄清 / Interrupt, await clarification |
| `aggregate_answers` | 外層 | 合成多個子答案 / Merge sub-answers |
| `orchestrator` | 內層 | 主推理引擎，決定工具調用 / Main reasoning engine |
| `tools` | 內層 | 執行工具（LangChain ToolNode）/ Execute tools |
| `should_compress_context` | 內層 | 決定是否壓縮 context / Decide if context needs compression |
| `compress_context` | 內層 | 壓縮訊息歷史以節省 token / Compress message history |
| `fallback_response` | 內層 | 達到迭代上限時的備援回答 / Fallback when iteration limit hit |
| `collect_answer` | 內層 | 收集最終答案 / Collect final answer |

---

## 3. 完整資料流程 | Complete Data Flow

```
使用者輸入問題 | User submits question
        │
        ▼
[summarize_history]
  過去訊息 <4 則 → 跳過 | Skip if <4 messages
  否則取最近 6 則 → 摘要為一段文字 | Otherwise summarize last 6 msgs
        │
        ▼
[rewrite_query]
  LLM 用結構化輸出（QueryAnalysis）分析：
  LLM uses structured output (QueryAnalysis) to analyze:
  • 問題是否清楚？| Is the question clear?
  • 拆成幾個子問題（最多3個）| Split into sub-questions (max 3)
        │
        ├── 不清楚 → [request_clarification] → interrupt → 使用者回覆後重新進 rewrite_query
        │            unclear → interrupt → user replies → re-enter rewrite_query
        │
        └── 清楚 → 用 Send() 平行啟動多個 agent subgraph（每個子問題一個）
                   clear → parallel Send() launches one agent subgraph per sub-question
                    │
                    ▼
             ┌─────────────────────────────────────────┐
             │   [orchestrator] (AgentState)            │
             │   LLM 強制先呼叫 search_child_chunks      │
             │   LLM forced to call search_child_chunks │
             └─────────────────────────────────────────┘
                    │ tool_calls 存在 | tool calls present
                    ▼
             [tools] ← ToolNode 執行以下工具 | ToolNode executes:
               • search_child_chunks(query, limit)
                 → Qdrant Hybrid Search（dense + sparse BM25）
                 → 回傳 child chunks + parent_id
                 → Returns child chunks + parent_id
               • retrieve_parent_chunks(parent_id)
                 → 從 JSON 檔案讀取完整 parent chunk
                 → Reads full parent chunk from JSON file
                    │
                    ▼
             [should_compress_context]
               計算目前 token 數（訊息 + context_summary）
               Calculate current tokens (messages + context_summary)
               • 超過 BASE_TOKEN_THRESHOLD + TOKEN_GROWTH_FACTOR × summary_tokens
                 → [compress_context]: 壓縮所有訊息為結構化摘要 → 回 orchestrator
                                       compress all messages into structured summary → back to orchestrator
               • 未超過 → 回 orchestrator 繼續推理
                          not exceeded → back to orchestrator to continue
                    │
             （迭代直到無 tool calls 或達上限 MAX_ITERATIONS / MAX_TOOL_CALLS）
             (iterate until no tool calls or hit MAX_ITERATIONS / MAX_TOOL_CALLS)
                    │
                    ├── 有最終答案 → [collect_answer] → 儲存 {index, question, answer}
                    │   has answer → store {index, question, answer}
                    └── 達上限 → [fallback_response] → 用已有 context 強制生成答案
                        hit limit → force-generate answer from available context
        │
        ▼（所有子問題完成後 | after all sub-questions done）
[aggregate_answers]
  LLM 將所有子答案合成為一篇自然流暢的回覆
  LLM synthesizes all sub-answers into one natural, flowing response
        │
        ▼
[ChatInterface] 串流輸出至 Gradio UI
[ChatInterface] streams output to Gradio UI
```

---

## 4. 最重要的檔案 | Most Important Files

修改時應重點關注的檔案，按影響範圍排序：
Files to focus on when making changes, ordered by impact:

| 優先順序 Priority | 檔案 File | 為什麼重要 Why It Matters |
|---|---|---|
| ⭐⭐⭐ | `rag_agent/graph.py` | Graph 的骨架——所有 nodes/edges 在這裡連線。改流程就改這裡。<br>Graph skeleton — all nodes/edges are wired here. Change the flow here. |
| ⭐⭐⭐ | `rag_agent/nodes.py` | 所有 node 的實際邏輯，包含核心推理、壓縮、fallback。<br>All actual node logic: core reasoning, compression, fallback. |
| ⭐⭐⭐ | `rag_agent/prompts.py` | 控制 LLM 行為的所有提示詞。想調整輸出品質、格式、語氣，改這裡最快。<br>All prompts controlling LLM behavior. Fastest way to tune output quality. |
| ⭐⭐ | `config.py` | 調整 token 上限、迭代次數、chunk 大小、模型名稱等關鍵參數。<br>Tune token limits, iterations, chunk sizes, model names. |
| ⭐⭐ | `rag_agent/edges.py` | 條件路由邏輯，決定 graph 走哪條路。<br>Conditional routing — decides which path the graph takes. |
| ⭐⭐ | `rag_agent/graph_state.py` | 兩個 State 的欄位定義，新增狀態欄位要改這裡。<br>Field definitions for both States — add new state fields here. |
| ⭐ | `core/chat_interface.py` | 控制 UI 的串流顯示方式（哪些 node 顯示、如何格式化）。<br>Controls how streaming appears in the UI. |
| ⭐ | `rag_agent/tools.py` | 定義可用工具，若要新增搜尋策略或工具，改這裡。<br>Tool definitions — add new retrieval strategies here. |
| ⭐ | `document_chunker.py` | 控制 parent/child chunk 的切割策略，影響檢索品質。<br>Controls chunking strategy, directly affects retrieval quality. |

**一句話總結 | TL;DR:**

> 想調行為 → `prompts.py`；想加功能 → `graph.py` + `nodes.py`；想調效能 → `config.py`；想改搜尋 → `tools.py` + `document_chunker.py`
>
> Tune behavior → `prompts.py`; Add features → `graph.py` + `nodes.py`; Tune performance → `config.py`; Improve retrieval → `tools.py` + `document_chunker.py`

---

## 5. 環境需求與啟動方式 | Environment Requirements & Setup

### 預設 LLM | Default LLM

這個專案預設使用**本地 Ollama**，不需要任何雲端 API key。
The project defaults to **local Ollama** — no cloud API key required.

設定位置 `config.py`：

```python
LLM_MODEL = "qwen3:4b-instruct-2507-q4_K_M"   # 本地 Ollama 模型 | Local Ollama model
DENSE_MODEL = "sentence-transformers/all-mpnet-base-v2"  # HuggingFace，自動下載 | Auto-downloaded
SPARSE_MODEL = "Qdrant/bm25"                   # 本地計算 | Computed locally
```

### 最少需要準備什麼 | Minimum Requirements

| 項目 Item | 是否必須 Required | 說明 Notes |
|-----------|-----------------|------------|
| **Ollama** | 必須 | 安裝並啟動本地 LLM 服務 / Install and run local LLM service |
| **Ollama 模型** | 必須 | `ollama pull qwen3:4b-instruct-2507-q4_K_M` |
| **Python 依賴** | 必須 | 安裝 requirements / Install requirements |
| **Qdrant** | 自動 | 使用本地嵌入模式（`QDRANT_DB_PATH`），不需另開服務 / Embedded mode, no separate service needed |
| **雲端 API Key** | 不需要 | 預設全部本地運行 / All local by default |
| **Langfuse** | 可選 | `.env` 預設關閉（`LANGFUSE_ENABLED=false`）/ Disabled by default |

### 啟動步驟 | Quick Start

```bash
# 1. 拉取 Ollama 模型 | Pull the Ollama model
ollama pull qwen3:4b-instruct-2507-q4_K_M

# 2. 安裝 Python 依賴 | Install dependencies
pip install -r requirements.txt

# 3. 啟動應用程式 | Start the app
python project/app.py
```

### 如何更換 LLM | Switching to a Different LLM

**換成其他 Ollama 模型**（最簡單）：只需修改 `config.py` 第 17 行：

```python
LLM_MODEL = "你的模型名稱"   # 例如 llama3.2、gemma3 等
```

**換成雲端服務（OpenAI、Anthropic 等）**：除了改 `config.py` 的模型名稱外，還需要：
1. 在 `rag_agent/nodes.py` 找到初始化 LLM 的地方（目前使用 `ChatOllama`）
2. 替換成對應的 LangChain wrapper，例如 `ChatOpenAI`、`ChatAnthropic`
3. 在 `.env` 中設定對應的 API key
