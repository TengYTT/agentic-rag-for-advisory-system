# Test Questions for Australian Study Abroad Advisory System

This file contains 17 test questions used for evaluating the Agentic RAG
advisory system. Questions are presented in bilingual format (English /
Traditional Chinese) to support both RAGAS evaluation (English) and
demonstration to Chinese-speaking users (Chinese).

- Category 1 (Q1–Q10): Baseline test questions for vanilla vs. enhanced
  comparison. Each question requires 1–2 source documents.
- Category 2 (Q11a–Q16): Demo questions requiring multi-source integration
  or external web search.

---

## Category 1: Baseline Test Questions
*Category 1：Baseline 測試用問題（小範圍、單一來源）*

### Admission Eligibility
*入學資格*

### Q1
**EN:** As an international student with an undergraduate background in Business (Marketing), do I meet the admission requirements for the UTS Master of Information Technology?
**ZH:** 我是國際學生，大學讀商科（行銷）背景，想申請 UTS Master of IT，我符合入學資格嗎？

### Q2
**EN:** For students without an IT background applying to the UNSW Master of Information Technology, what prerequisite courses are required? Are students with a GPA below 3.0 eligible to apply?
**ZH:** 非 IT 背景的學生申請 UNSW Master of IT，需要補修哪些先修課程？GPA 不到 3.0 的學生可以申請嗎？

### Q3
**EN:** What are the key differences between the UTS Master of Information Technology and the UNSW Master of Information Technology?
**ZH:** UTS MIT 和 UNSW MIT 有什麼差別？

### Q4
**EN:** What are the English language proficiency requirements for the UTS and UNSW Master of Information Technology programs? For an applicant with average English proficiency, which program would be the more advisable primary application target?
**ZH:** UTS MIT 和 UNSW MIT 的英文門檻需要幾分？如果我的英文程度比較一般的話，建議以哪一個為主要的申請目標？

---

### Tuition & Timeline
*費用與時程*

### Q5
**EN:** Please provide a comparison of the international student tuition fees for the UTS and UNSW Master of Information Technology programs.
**ZH:** UTS MIT 和 UNSW MIT 國際學生的學費比較

### Q6
**EN:** What is the duration of the UTS and UNSW Master of Information Technology programs? Is part-time enrolment available for either program?
**ZH:** UTS MIT 和 UNSW MIT 課程是幾年制的？可以兼職就讀嗎？

### Q7
**EN:** What are the application deadlines for the UNSW Master of Information Technology in 2026? Is it still possible to submit an application at this stage? What is the earliest available intake for a current applicant? Does UNSW offer conditional admission?
**ZH:** UNSW MIT 2026 年的申請截止日期是什麼時候？現在申請來得及嗎？最快現在可以申請的是哪一個入學時間？有沒有開條件式錄取？

---

### Cross-source Comparison (Conflict Detection)
*跨來源對比（conflict detection 測試）*

### Q8
**EN:** I have encountered conflicting information regarding the English language requirements for the UNSW Master of Information Technology. What is the official IELTS requirement — 6.5 or 6.0 overall? What is the corresponding minimum PTE Academic score?
**ZH:** 我看到不同地方說的英文門檻不一樣，UNSW MIT 官方要求到底是雅思 6.5 還是 6.0？對應 PTE 要考多少分？

### Q9
**EN:** There appears to be a discrepancy between the student visa requirements stated by the Department of Home Affairs and those stated by the university. Which source should be considered the authoritative reference?
**ZH:** 移民局和學校說的學生簽證要求有出入，以哪個為準？

---

### Program Comparison
*課程比較（兩份文件）*

### Q10
**EN:** Please compare the UTS and UNSW Master of Information Technology programs, covering the differences in available specialisations, tuition fees, admission requirements, application deadlines, program characteristics, and the relative strengths and limitations of each institution.
**ZH:** 請比較 UTS 和 UNSW 的 Master of IT，列出課程方向、費用、入學門檻、申請截止日期、課程特色、學校優缺點等差異。

---

## Category 2: Demo Prototype Questions
*Category 2：Prototype Demo 展示用問題（跨多來源、需要完整知識庫）*

### Course Filtering & Integration
*課程篩選整合型*

### Q11a
**EN:** As an applicant without a cognate IT background, I am interested in IT-related postgraduate programs at Australian universities ranked within the global top 100. Could you list the available options and provide an overview of each program's specialisations, tuition fees, admission requirements, and application deadlines?
**ZH:** 我是非相關背景，想申請澳洲世界排名前百大的 IT 相關課程，請列出有哪些選項，並整理課程方向、費用、入學門檻、申請截止日期。

### Q11b
**EN:** As an applicant without a cognate IT background (with an undergraduate degree in [field]), which Australian master's programs in Information Technology or Computer Science would I be eligible to apply for? Are there any prerequisite subjects I would need to complete prior to enrolment?
**ZH:** 我是非相關背景（大學讀的是xxx），可以申請哪些澳洲的 IT、電腦科學相關碩士課程？有需要補修哪些科目嗎？

### Q12
**EN:** Which Australian universities offer a Master of Data Science? Among these, which institutions are most accessible to applicants without a prior IT background?
**ZH:** 澳洲有哪些大學提供 Data Science 碩士？哪幾間對非 IT 背景最友善？

---

### Visa & Migration Integration
*簽證與移民整合型*

### Q13
**EN:** Upon completing the UTS Master of Information Technology, what post-study migration pathways are available? What are the eligibility requirements for each pathway?
**ZH:** 讀完 UTS Master of IT 之後，我有哪些移民路徑可以走？每條路徑需要什麼條件？

### Q14
**EN:** What documents are required for a Student Visa (Subclass 500) application, and what is the standard application process?
**ZH:** 學生簽證 500 需要準備哪些文件？申請流程是什麼？

### Q15
**EN:** How many years does the Temporary Graduate Visa (Subclass 485) grant? Is there a difference in post-study work entitlement between completing a two-year and a three-year master's program?
**ZH:** 畢業生簽證（485）可以拿幾年？讀兩年碩士和三年碩士有差別嗎？

---

### Temporal Relevance Test
*時效性測試（retrieved date 功能）*

### Q16
**EN:** Is the information provided by this system current? What year does the underlying data refer to? If the official university websites have since been updated, is the system capable of prompting me to verify the latest information directly?
**ZH:** 這些資訊是最新的嗎？是哪一年的資料？如果官網有更新，系統能否提示我去確認？

---

## Translation Notes & Test Design Rationale

This section documents intentional design choices in the test questions,
particularly cases where a question contains implicit assumptions, scale
mismatches, or factual nuances that the system is expected to recognise
and address. These notes serve as evaluation rubric anchors.

### Q2 — GPA vs WAM Scale Mismatch
UNSW does not use GPA scale — its official admission standard is the Weighted
Average Mark (WAM), expressed as a percentage with a minimum threshold of 65%.
The question uses "GPA below 3.0" (a 4.0-scale metric common in Taiwan and the
US), which does not map directly to UNSW's stated requirement. This is an
intentional mismatch designed to test whether the system correctly identifies
the scale difference and translates or flags the discrepancy, rather than
treating 3.0/4.0 and 65% WAM as equivalent.

### Q4 — "Average English Proficiency" Interpretation
The phrase "英文程度比較一般" (average English proficiency) is intentionally
ambiguous. It is interpreted here as an applicant who can meet the lower of the
two programs' thresholds but may struggle to meet the higher one. This
interpretation is meaningful because UTS and UNSW have different TOEFL iBT
requirements (UTS: 79; UNSW: 90) — an 11-point gap that is significant for
borderline applicants. The question is designed to test whether the system
surfaces this specific difference and provides a recommendation grounded in the
score comparison, rather than giving a generic answer.

### Q11 — Original Compound Question (Split into Q11a and Q11b)
The original Chinese file contained two distinct sub-questions under Q11 without
clear sub-numbering. They have been split into Q11a (multi-source integration
with global ranking filter) and Q11b (background-based eligibility with
prerequisite knowledge), since they test different system capabilities. Q11a
requires the system to cross-reference ranking data with program eligibility for
non-cognate applicants across multiple institutions. Q11b requires the system to
assess eligibility given an unspecified undergraduate background and return
prerequisite or pathway information. The two sub-questions are retained as
separate test cases to allow independent RAGAS scoring.

### Q15 — 485 Visa Duration Based on Location, Not Program Length
The question asks whether completing a two-year versus a three-year master's
program affects the Temporary Graduate Visa (Subclass 485) duration. Under
current Department of Home Affairs policy, the 485 visa duration for graduates
studying in a major city (Sydney, Melbourne, Brisbane) is 2 years regardless of
program length; for regional study, an additional 2-year extension (totalling 4
years) may apply. Program length does not directly determine visa duration. This
question tests whether the system correctly identifies the location-based rule
and avoids the common misconception that a longer program automatically yields a
longer post-study visa.

---

## Scoring Rubric
*評分說明*

每個問題在 baseline 和 enhanced 版本各跑一次，記錄：
- 回答是否正確
- 是否有引用來源
- 是否標示不確定性
- RAGAS 分數（faithfulness、answer_relevancy）
