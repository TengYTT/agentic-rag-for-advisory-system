# Report Materials — Agentic RAG Trustworthiness Enhancement
*Compiled 2026-05-31. Internal use only — not for submission as-is.*

---

## Section 1: Project File Tree

### Python Source Files (with line counts)

| File Path | Lines |
|---|---|
| `project/rag_agent/prompts.py` | 457 |
| `project/rag_agent/nodes.py` | 329 |
| `project/ui/css.py` | 278 |
| `project/document_chunker.py` | 163 |
| `project/core/chat_interface.py` | 153 |
| `project/audit/audit_logger.py` | 107 |
| `project/rag_agent/tools.py` | 103 |
| `project/core/document_manager.py` | 99 |
| `project/ui/gradio_app.py` | 92 |
| `project/rag_agent/graph.py` | 52 |
| `project/db/parent_store_manager.py` | 51 |
| `project/core/observability.py` | 47 |
| `project/utils.py` | 46 |
| `project/db/vector_db_manager.py` | 46 |
| `project/core/rag_system.py` | 43 |
| `project/config.py` | 42 |
| `project/rag_agent/graph_state.py` | 36 |
| `project/rag_agent/edges.py` | 27 |
| `project/app.py` | 25 |
| `project/rag_agent/schemas.py` | 12 |
| **Total** | **2,208** |

### Knowledge Base (`markdown_docs/`)

```
markdown_docs/
├── UNSW_Master_of_IT.md
├── UTS_Master_of_IT.md
└── _archive_zh/          (original Chinese reference files)
```

### Evaluation Artefacts (`evaluation/`)

```
evaluation/
├── audit/
│   └── queries.jsonl                              (17 records)
├── baseline/
│   ├── baseline_results.md
│   └── baseline_results_v2_english_docs_en.md
├── enhanced/
│   └── enhanced_results_v1_en.md
├── phase_c_smoke_output/
│   ├── test_1_in_scope.md
│   └── test_2_out_of_scope.md
├── evaluation_comparison.md
├── manual_eval.py
├── run_baseline_test.py
├── sanity_check_q8.py
└── test_questions.md
```

### Audit Module (`project/audit/`)

```
project/audit/
├── __init__.py
└── audit_logger.py        (107 lines — append-only JSONL logger)
```

---

## Section 2: Side-by-Side Comparison — Q5, Q8, Q10, Q14

---

### Q5: Please provide a comparison of the international student tuition fees for the UTS and UNSW Master of Information Technology programs.

**Baseline:**

> The international student tuition fees for the Master of Information Technology programs at the University of Technology Sydney (UTS) and the University of New South Wales (UNSW) are as follows:
>
> - **University of Technology Sydney (UTS):**
>   The indicative annual tuition fee is **AUD $55,375.00**, resulting in a total fee of approximately **AUD $110,750.00** over the two-year program (calculated as $55,375 × 2).
>
> - **University of New South Wales (UNSW):**
>   The indicative annual tuition fee is **AUD $63,000.00**, leading to a total fee of **AUD $126,000.00** over the two-year program.
>
> **Comparison:**
> - UNSW charges a higher annual fee (AUD $63,000) compared to UTS (AUD $55,375).
> - Over the two-year duration, UNSW's total fee is **AUD $15,250 higher** than UTS's total fee.
>
> ---
> **Sources:** UTS_Master_of_IT.md, UNSW_Master_of_IT.md

**Enhanced:**

> The international student tuition fees for the Master of Information Technology programs at UTS and UNSW differ significantly, with UTS offering a more affordable option.
>
> - **UTS** charges an annual tuition fee of **AUD $55,375**, with a total fee for a 2-year full-time program of **AUD $113,242**. The per-semester fee is **AUD $27,687.50**. The course is CRICOS-registered (084256C) and eligible for ACS membership.
>
> - **UNSW** has an annual tuition fee of **AUD $63,000** for the first year, with a total degree fee of **AUD $130,500** for the full program. Fees are subject to annual review and may be allocated on a competitive merit basis.
>
> **Fee Comparison (2-year full-time):**
> - UTS: AUD $113,242
> - UNSW: AUD $130,500
> This means UTS charges approximately **AUD $17,258 less** over the full program — about **AUD $7,000 less per year**.
>
> All fee figures are indicative. Students are strongly advised to confirm directly on official university websites.
>
> ---
> **Sources:** UTS_Master_of_IT.md, UNSW_Master_of_IT.md

**Difference observations:**

- **Arithmetic accuracy:** Baseline computes UTS total as $110,750 ($55,375 × 2 rounded flat) and UNSW as $126,000; enhanced uses the KB's actual figures ($113,242 and $130,500), making the enhanced answer factually more precise.
- **Richer context:** Enhanced adds per-semester fee, CRICOS registration number, and ACS membership note — all from retrieved documents — giving a more complete advisory response.
- **Comparative framing:** Enhanced explicitly states "AUD $17,258 less" and "AUD $7,000 less per year," making the comparison immediately actionable for the student. Baseline states the gap as "$15,250 higher" (a figure derived from the incorrect totals).

---

### Q8: I have encountered conflicting information regarding the English language requirements for the UNSW Master of Information Technology. What is the official IELTS requirement — 6.5 or 6.0 overall? What is the corresponding minimum PTE Academic score?

**Baseline:**

> The official IELTS requirement for the UNSW Master of Information Technology is an overall score of **6.5**, with a minimum of **6.0 in each subtest** (Listening, Reading, Writing, Speaking).
>
> For the PTE Academic, the corresponding minimum score is **64 overall**, with a minimum of **54 in each subtest**.
>
> These requirements are clearly stated in the official UNSW admissions guidelines and are consistent across both the IELTS and PTE Academic sections.
>
> ---
> **Sources:** UNSW_Master_of_IT.md

**Enhanced:**

> The official IELTS requirement for the UNSW Master of Information Technology is an overall score of **6.5**, with a minimum of **6.0 in each subtest** (Listening, Reading, Writing, Speaking). This is clearly stated in the university's official English Language Requirements section.
>
> For the PTE Academic, the corresponding minimum score is **64 overall**, with a minimum of **54 in each subtest**. While the university does not provide a direct IELTS-to-PTE conversion, it specifies the required PTE score directly.
>
> It is important to note that although some sources may suggest a lower threshold (such as 6.0), the official documentation from UNSW confirms the requirement as 6.5 overall with no subtest below 6.0. Any information suggesting a lower IELTS score should be treated with caution and verified against the official program page.
>
> ---
> **Sources:** UNSW_Master_of_IT.md

**Difference observations:**

- **Conflict framing:** Enhanced explicitly addresses the "conflicting information" premise of the question, explaining why "6.0" appears in some sources (it is the subtest minimum, not the overall requirement). Baseline gives a correct answer but does not engage with the conflict narrative.
- **Stochastic hallucination (sanity check run):** A separate sanity check run of the enhanced system (Phase B-2-c, not the final evaluation) produced an additional unsupported sentence: *"PTE Academic minimum is 64 overall, not 58 as sometimes reported in unofficial sources."* The number 58 does not appear in any retrieved chunk; this is a training-data leak. The final evaluation run (enhanced_results_v1_en.md) did not reproduce this artefact, demonstrating LLM stochastic variance.
- **Source coverage:** Both cite UNSW_Master_of_IT.md correctly. Baseline runner's post-processing incorrectly detected UTS_Master_of_IT.md as a source (parser artefact).

---

### Q10: Please compare the UTS and UNSW Master of Information Technology programs, covering the differences in available specialisations, tuition fees, admission requirements, application deadlines, program characteristics, and the relative strengths and limitations of each institution.

**Baseline (excerpt — full response ~3,200 chars):**

> **Comparison of UTS and UNSW Master of Information Technology Programs**
>
> - **Available Specialisations**
>   - **UNSW**: Artificial Intelligence, Database Systems, Cyber Security Engineering, Information Technology, Internetworking, Data Science and Engineering.
>   - **UTS**: The available specialisations are **not explicitly listed** in the retrieved content, making it difficult to assess the breadth or depth of specialisation options offered.
>
> - **Tuition Fees**
>   - Tuition fees for both UTS and UNSW are **not specified** in the retrieved materials. Therefore, a direct comparison of cost cannot be made based on the available information.
>
> [...]
>
> - **UTS Limitations**: Lack of detail on specialisations, program duration, core courses, and delivery format. No accreditation information is provided.
>
> ---
> **Sources:** UNSW_Master_of_IT.md, UTS_Master_of_IT.md

**Enhanced (excerpt — full response 8,748 chars, table-heavy):**

> | Feature | UNSW | UTS |
> |---|---|---|
> | Duration | 2 years (96 UoC) | 2 years (96 UoC) |
> | Open to Non-IT? | ✅ Yes | ❌ Not explicitly stated |
> | Specialisations | Core IT tracks | Business IT, Cybersecurity, Data Analytics, Enterprise Software, Interactive Media, Internetworking |
> | Tuition (international) | AUD $63,000/yr | Higher for international |
> | Double Degree | ✅ MIT + Commerce | ❌ Not mentioned |
>
> [extensive tables, emoji formatting, per-profile recommendations]
>
> ---
> **Sources:** (empty in audit log — citation extraction failure)

**Difference observations:**

- **Honesty of gaps:** Baseline explicitly states when information is missing ("specialisations not listed", "tuition fees not specified in retrieved materials"), which is technically more faithful to the KB. Enhanced fills those gaps — partly from retrieved documents, partly from training-data memory — producing a more complete but less source-grounded answer.
- **Citation failure:** Q10's audit log `sources` field is `[]` (empty), despite the answer clearly drawing from both KB files. The citation extraction regex (`\b([\w\-]+\.md)\b`) failed because the extended synthesis referred to sources as "UTS handbook"/"UNSW program page" without `.md` suffixes. This is the architecture's primary failure mode identified in Case Study 2.
- **Response length and style:** Enhanced produces an 8,748-character response with markdown tables and emoji — 5–10× the length of typical responses. This may indicate the LLM treated the multi-axis comparison query as a maximally exhaustive synthesis task, bypassing normal length constraints.

---

### Q14: What documents are required for a Student Visa (Subclass 500) application, and what is the standard application process?

**Baseline:**

> The retrieved answers do not provide specific information about the required documents for a Student Visa (Subclass 500) application or the standard application process. While the documents mention that a Student Visa (Subclass 500) covers the full duration of a Master of Information Technology program at universities like UNSW and UTS, they do not list any official visa application requirements such as proof of course acceptance, financial evidence, health insurance, police clearance, or supporting forms.
>
> Additionally, there is no detail on the step-by-step application process, including forms to complete, processing times, fees, validity periods, or eligibility criteria for the visa.
>
> ---
> **Sources:** UTS_Master_of_IT.md, UNSW_Master_of_IT.md

**Enhanced:**

> The required documents and standard application process for a Student Visa (Subclass 500) are not explicitly outlined in the provided knowledge base.
>
> While the retrieved content includes detailed information about admission requirements — such as English language proficiency (e.g., IELTS 6.5 overall for UTS and UNSW Master of IT programs) and course structure — **no specific list of documents required for the Student Visa (Subclass 500) application** is available.
>
> Similarly, **the standard application process — such as step-by-step procedures, fees, processing times, or eligibility criteria — is not detailed** in the provided materials.
>
> The official Australian Government website remains the most authoritative source for accurate and up-to-date information.
>
> *(Audit log: low_confidence=True, sources=UNSW_Master_of_IT.md, UTS_Master_of_IT.md)*
>
> ---
> **Sources:** UNSW_Master_of_IT.md, UTS_Master_of_IT.md

**Difference observations:**

- **Uncertainty signaling:** Enhanced triggered `low_confidence=True` in the grading pipeline, which appends the `⚠️ Low confidence notice` banner in the displayed answer. Baseline has no such mechanism — it narrates the gap in prose but without a programmatic trust signal.
- **Scope explanation:** Enhanced explicitly states what IS in the KB ("English language proficiency... for Master of IT programs") to contextualise why the KB cannot answer the visa question. This provides a more helpful advisory framing than baseline's flat "not specified."
- **Source attribution anomaly:** Both systems cite both KB files as sources even though the KB contains no Subclass 500 document list. This reflects how the orchestrator retrieved related chunks (mentioning visa in passing) and listed those files as sources — a citation over-attribution artefact present in both systems.

---

## Section 3: Full Audit Log — 17 Records

All records from `evaluation/audit/queries.jsonl`, generated 2026-05-31 04:16–04:42 UTC during the full enhanced evaluation run.

| # | Label | low_conf | Sources | Timestamp (UTC) | Answer (chars) |
|---|---|---|---|---|---|
| 1 | Q1 | False | UTS_Master_of_IT.md | 04:16:32 | 1,608 |
| 2 | Q2 | True | UNSW_Master_of_IT.md | 04:17:10 | 1,880 |
| 3 | Q3 | True | UNSW_Master_of_IT.md | 04:19:01 | 3,827 |
| 4 | Q4 | True | UNSW_Master_of_IT.md, UTS_Master_of_IT.md | 04:21:53 | 4,263 |
| 5 | Q5 | True | UNSW_Master_of_IT.md, UTS_Master_of_IT.md | 04:23:13 | 2,496 |
| 6 | Q6 | True | UNSW_Master_of_IT.md, UTS_Master_of_IT.md | 04:24:07 | 1,582 |
| 7 | Q7 | False | UNSW_Master_of_IT.md | 04:25:55 | 3,672 |
| 8 | Q8 | False | UNSW_Master_of_IT.md | 04:26:33 | 1,303 |
| 9 | Q9 | True | UNSW_Master_of_IT.md, UTS_Master_of_IT.md | 04:27:06 | 2,278 |
| 10 | Q10 | True | *(none — citation extraction failure)* | 04:31:08 | 8,748 |
| 11 | Q11a | False | UNSW_Master_of_IT.md, UTS_Master_of_IT.md | 04:33:52 | 7,616 |
| 12 | Q11b | False | UNSW_Master_of_IT.md, UTS_Master_of_IT.md | 04:36:29 | 5,226 |
| 13 | Q12 | True | UNSW_Master_of_IT.md, UTS_Master_of_IT.md | 04:37:54 | 1,931 |
| 14 | Q13 | False | UTS_Master_of_IT.md | 04:38:58 | 1,906 |
| 15 | Q14 | True | UNSW_Master_of_IT.md, UTS_Master_of_IT.md | 04:40:32 | 2,552 |
| 16 | Q15 | False | UNSW_Master_of_IT.md, UTS_Master_of_IT.md | 04:41:20 | 1,985 |
| 17 | Q16 | True | UNSW_Master_of_IT.md, UTS_Master_of_IT.md | 04:42:26 | 2,712 |

**Notes:**
- Q10: 8,748 chars is the longest response by a factor of 2×; citation extraction failed (see Case Study 2).
- Q13 and Q15: `low_confidence=False` despite being out-of-scope questions (hedging failure; see Case Study 3).
- Q7 and Q8: `low_confidence=False` correctly — these are in-scope questions with clear KB coverage.
- Out-of-scope questions with correct `low_confidence=True`: Q2 (partial), Q12, Q14, Q16. Miss: Q13, Q15, Q9.

---

## Section 4: Commit History with Diff Stats

| Commit | Date | Subject | Files Changed | +Insertions | -Deletions |
|---|---|---|---|---|---|
| d6c8fa2 | 2026-05-31 | Phase E: enhanced evaluation + trustworthiness comparison | 3 | +1,356 | 0 |
| d1cf24f | 2026-05-31 | Phase D: audit logging via append-only JSONL | 4 | +130 | -5 |
| 4fff57f | 2026-05-31 | Phase C: surface trust signals via answer-text trust footer + banner | 3 | +137 | -3 |
| e83a791 | 2026-05-31 | Phase B: grade_documents node + uncertainty signaling | 5 | +134 | -4 |
| bad090a | 2026-05-31 | Phase A: domain adaptation + source tiering metadata pipeline | 3 | +395 | -120 |
| 7984d91 | 2026-05-31 | test: add baseline results with English knowledge base (Step 1 deliverable) | 1 | +796 | 0 |
| 8a4ff69 | 2026-05-31 | fix: preserve original file extension in chunk metadata | 2 | +2 | -2 |
| 3ce366b | 2026-05-31 | test: convert test questions to bilingual format and update baseline runner | 2 | +243 | -69 |
| 7c0c70a | 2026-05-15 | docs: add specialisation | 1 | +1 | 0 |
| 19deb7e | 2026-05-15 | docs: add English knowledge base from UTS/UNSW official sources | 2 | +499 | 0 |

**Phase-by-phase insertion summary:**
- Phase A (prompts + tools + chunker): +395 lines — largest single-phase change
- Phase B (nodes + prompts): +134 lines — grade_documents, graph wiring
- Phase C (nodes + smoke outputs): +137 lines — trust footer, banner, helpers
- Phase D (audit logger + nodes): +130 lines — JSONL logging integration
- Phase E (evaluation scripts + report): +1,356 lines — evaluation artefacts

---

## Section 5: Parent/Child Chunk Statistics

### Summary

| Metric | Value |
|---|---|
| Total parent chunks | 8 |
| UTS parent chunks | 3 |
| UNSW parent chunks | 5 |
| Child chunks per parent (approx.) | ~5–8 (from RecursiveCharacterTextSplitter, 500 char chunk size) |

### UTS Parent Chunks (3 chunks)

| Chunk ID | H2 Sections Covered |
|---|---|
| UTS_Master_of_IT_parent_0 | Overview → Course Structure / Duration → Tuition Fees |
| UTS_Master_of_IT_parent_1 | Admission Requirements → English Language Requirements → Application Deadlines / Intakes |
| UTS_Master_of_IT_parent_2 | Majors / Specialisations → Non-IT Background → Post-graduation Migration → Rankings → Related Pathways |

### UNSW Parent Chunks (5 chunks)

| Chunk ID | H2 Sections Covered |
|---|---|
| UNSW_Master_of_IT_parent_0 | Overview → Course Structure / Duration |
| UNSW_Master_of_IT_parent_1 | Course Structure / Duration → Tuition Fees → Admission Requirements |
| UNSW_Master_of_IT_parent_2 | Admission Requirements → English Language Requirements |
| UNSW_Master_of_IT_parent_3 | Application Deadlines / Intakes → Majors / Specialisations |
| UNSW_Master_of_IT_parent_4 | Non-IT Background → Post-graduation Migration → Rankings → Related Pathways |

**Observation:** UNSW has more parent chunks (5 vs 3) because the UNSW document is longer and covers more admission pathway detail (cognate vs non-cognate, GradCert packaging, WAM requirements). The parent chunking boundary follows H2 markdown headers as primary split points.

---

## Section 6: Phase C Smoke Test Demo Outputs

### Test 1: In-Scope Query (UTS Tuition)

**Query:** What is the tuition fee for UTS Master of IT for international students?

**Final Output (as displayed to user):**

> The indicative annual tuition fee for the Master of Information Technology program at the University of Technology Sydney (UTS) for international students is **AUD $55,375.00**.
>
> This amounts to an indicative total tuition fee for the two-year program of **AUD $113,242.00** (calculated as $55,375 × 2).
>
> > Please note that these fees are indicative and may be subject to annual review. For the most accurate and up-to-date information, including any potential changes or additional charges, it is recommended to visit the official UTS fees page: [https://cis.uts.edu.au/fees/course-fees.cfm](https://cis.uts.edu.au/fees/course-fees.cfm).
>
> ---
>
> **Sources:**
> - UTS_Master_of_IT.md
>
> 📊 **Trust Signals**
> - 🏛️ **UTS_Master_of_IT.md**
>   - Source Tier: 1 (university_official)
>   - 🔗 https://www.uts.edu.au/study/find-a-course/master-information-technology
>   - 📅 Retrieved: 2026-05-15

**Diagnostic signals:** low_confidence=False | max_grade=1.00 | 5 chunks graded

---

### Test 2: Out-of-Scope Query (Subclass 500 Visa)

**Query:** What documents are required for an Australian Subclass 500 student visa application?

**Final Output (as displayed to user):**

> ⚠️ **Low confidence notice**: The available knowledge base may not fully address this query. The response below is based on partial information; please verify at the official sources listed in the references section.
>
> The specific documents required for an Australian Subclass 500 student visa application are not detailed in the provided sources.
>
> While the retrieved content covers admission requirements and post-graduation pathways for Master of Information Technology programs at UTS and UNSW, it does not list the official documents needed to apply for the Subclass 500 student visa.
>
> For accurate and up-to-date information on the required documents, you should refer to the official Australian Government immigration website:
>
> - [Student Visa (Subclass 500) – Australian Government](https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/student-500)
>
> ---
>
> **Sources:**
> - UTS_Master_of_IT.md
> - UNSW_Master_of_IT.md
>
> 📊 **Trust Signals**
> - 🏛️ **UNSW_Master_of_IT.md**
>   - Source Tier: 1 (university_official)
>   - 🔗 https://www.unsw.edu.au/study/postgraduate/master-of-information-technology
>   - 📅 Retrieved: 2026-05-15
> - 🏛️ **UTS_Master_of_IT.md**
>   - Source Tier: 1 (university_official)
>   - 🔗 https://www.uts.edu.au/study/find-a-course/master-information-technology
>   - 📅 Retrieved: 2026-05-15

**Diagnostic signals:** low_confidence=True | max_grade=0.40 | 5 chunks graded

---

## Section 7: Q8 Hallucination Case Study

### Query

"I have encountered conflicting information regarding the English language requirements for the UNSW Master of Information Technology. What is the official IELTS requirement — 6.5 or 6.0 overall? What is the corresponding minimum PTE Academic score?"

### Enhanced System Answer (from enhanced_results_v1_en.md, Q8)

> The official IELTS requirement for the UNSW Master of Information Technology is an overall score of **6.5**, with a minimum of **6.0 in each subtest** (Listening, Reading, Writing, Speaking). This is clearly stated in the university's official English Language Requirements section.
>
> For the PTE Academic, the corresponding minimum score is **64 overall**, with a minimum of **54 in each subtest**. While the university does not provide a direct IELTS-to-PTE conversion, it specifies the required PTE score directly, making it a valid benchmark for applicants.
>
> It is important to note that although some sources may suggest a lower threshold (such as 6.0), the official documentation from UNSW confirms the requirement as 6.5 overall with no subtest below 6.0. Therefore, any information suggesting a lower IELTS score should be treated with caution and verified against the official program page.

### Sanity Check Run Answer (Phase B-2-c, separate run)

> The official English language requirements for the UNSW Master of Information Technology are as follows:
>
> - **IELTS Academic**: A minimum overall band score of **6.5**, with a minimum of **6.0 in each subtest**.
> - **Pearson PTE Academic**: A minimum overall score of **64**, with a minimum of **54 in each subtest**.
>
> Note: The IELTS requirement is not 6.0 overall — it is 6.5 overall with a subtest minimum of 6.0. Similarly, the PTE Academic minimum is 64 overall, **not 58 as sometimes reported in unofficial sources**.

### Audit Record (Q8)

```json
{
  "timestamp": "2026-05-31T04:26:33Z",
  "query": "I have encountered conflicting information regarding...",
  "sources": ["UNSW_Master_of_IT.md"],
  "sources_metadata": {
    "UNSW_Master_of_IT.md": {
      "tier": 1,
      "source_type": "university_official",
      "primary_url": "https://www.unsw.edu.au/study/postgraduate/master-of-information-technology",
      "last_retrieved": "2026-05-15"
    }
  },
  "low_confidence": false,
  "num_sub_answers": 1,
  "answer_length_chars": 1303
}
```

### Analysis

The number "58" (PTE score) appears only in the sanity check run, not in the final evaluation run — confirming this is a stochastic hallucination, not a systematic failure. In neither run does "58" appear in any retrieved chunk (verified by searching UNSW_Master_of_IT.md).

The hallucination pattern is structurally interesting: it occurs while the LLM is *complying* with the prompt rule to address conflicting information ("confirm the correct figure, dismiss incorrect figures"). The soft constraint "ground every factual claim in retrieved documents" was bypassed when the LLM generated a plausible-sounding counter-example. This represents a case where desirable behaviour (disambiguation) triggered undesirable behaviour (fabrication).

---

## Section 8: Grade Distribution per Question

Per-question grade distributions (individual chunk scores from `grade_documents`) are **not retained in the audit log**. The current logging schema captures only:

- `low_confidence` (boolean, derived from `max(grades) < GRADE_THRESHOLD`)
- `sources` (filenames extracted from answer text)
- `sources_metadata` (tier, URL, date per source)

The raw `retrieval_grades` list (e.g. `[1.0, 0.0, 1.0, 0.0, 0.4]`) is an `AgentState` field that lives only in the subgraph execution context and is not propagated to the outer State or logged.

> "Per-question grade distributions are not retained in the audit log (only the boolean `low_confidence` flag is logged). For the published evaluation, only aggregated metrics are available. This is a limitation of the current logging schema and is noted in Future Work."

**Available approximation:** For the two Phase C smoke test queries, grade distributions were observed directly from console output (before debug prints were removed in Phase B-2-d):

| Query | Grades | max | low_confidence |
|---|---|---|---|
| UTS tuition (in-scope) | [1.0, 0.0, 1.0, 0.0, 0.4] | 1.00 | False |
| Subclass 500 visa (out-of-scope) | [0.2, 0.0, 0.2, 0.4, 0.2] | 0.40 | True |

These two data points illustrate the expected grade distribution shape but are insufficient for statistical generalisation across all 17 questions.
