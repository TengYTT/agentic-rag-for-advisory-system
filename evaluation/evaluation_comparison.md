# Evaluation Comparison: Baseline vs Enhanced

## Test Set
- 17 bilingual test questions (English used here)
- Knowledge base: UTS_Master_of_IT.md, UNSW_Master_of_IT.md (both Tier 1)
- Out-of-scope questions: ['Q12', 'Q13', 'Q14', 'Q15', 'Q16', 'Q9']
- See `evaluation/test_questions.md` for full set

## Quantitative Trustworthiness Metrics

| Metric | Baseline (vanilla) | Enhanced | Δ |
|---|---|---|---|
| **Citation Recall** | 100.0% (17/17) | 94.1% (16/17) | **-5.9%** |
| **Hedging Rate (out-of-scope, n=6)** | 0.0% (mechanism absent) | 66.7% (4/6) | **+66.7%** |
| **Source Tier Coverage** | 0.0% (mechanism absent) | 94.1% | **+94.1%** |
| **Multi-source Synthesis (avg sources/Q)** | 1.71 | 1.53 | **-0.18** |

## Interpretation

### Citation Recall
Baseline cites sources for 17/17 questions. 0 questions have no source attribution — a key trustworthiness gap.
Enhanced cites sources for 16/17 questions, an improvement of -5.9%.

### Hedging Rate
The vanilla baseline has no uncertainty signaling mechanism. The enhanced system triggers low_confidence on 4/6 out-of-scope questions, demonstrating that the grading-based confidence assessment correctly flags queries the knowledge base cannot reliably support.

### Source Tier Coverage
The enhanced system exposes tier metadata for 94.1% of queries, enabling users to assess source authority. The baseline has no such mechanism.

### Multi-source Synthesis
Both systems cite an average of ~1.53 sources per question, indicating the enhancement layer preserves the baseline's cross-source synthesis ability while adding trust metadata.

## Qualitative Case Studies

The quantitative metrics above are complemented by 4 case studies that reveal
both the strengths and structural limitations of the trustworthiness
enhancement layer. These cases serve as the empirical basis for the
Discussion and Limitations sections of the project report.

### Case 1: Q8 — Soft-constraint failure (training-data leak)

**Query:** "I have encountered conflicting information regarding the English
language requirements for the UNSW Master of Information Technology. What is
the official IELTS requirement — 6.5 or 6.0 overall? What is the corresponding
minimum PTE Academic score?"

**Observed behaviour:** The enhanced system correctly disambiguated the
6.5/6.0 conflict (overall vs sub-band) and provided the verified PTE 64/54
figures. However, the answer also included an unsupported reference:
*"PTE Academic minimum is 64 overall, not 58 as sometimes reported in
unofficial sources."* The number 58 does not appear in any retrieved chunk.

**Significance:** The hallucination occurred while the system was
*following* the rule to acknowledge conflicts — a desirable behaviour. The
prompt rule "ground every factual claim in the retrieved documents" acted
as a soft constraint that the LLM rationalised away when augmentation
seemed helpful. This illustrates a fundamental property of prompt-based
trustworthiness: the rules are guidance, not enforcement.

---

### Case 2: Q10 — Citation extraction failure on extended synthesis

**Query:** "Please compare the UTS and UNSW Master of Information Technology
programs, covering the differences in available specialisations, tuition fees,
admission requirements, application deadlines, program characteristics, and
the relative strengths and limitations of each institution."

**Observed behaviour:**
- Answer length: 8,748 characters (5–10× larger than typical responses)
- low_confidence: True (grading correctly flagged retrieval noise)
- Audit log `sources`: [] (empty)

**Significance:** The empty sources field is misleading: the LLM clearly
synthesized information from both knowledge base documents (the answer
discusses UTS and UNSW factual content extensively). The citation
extraction mechanism — `re.findall(r"\b([\w\-]+\.md)\b", text)` — relies
on the LLM verbatim emitting filename tokens. In the extended synthesis,
the LLM described sources as "UTS handbook" / "UNSW program page" without
the `.md` suffix.

This is a **second instance of soft-constraint failure**, structurally
analogous to Case 1: the aggregation prompt instructs the LLM to cite
filenames, but extended generation breaks this contract. The architecture
should propagate citation identity through state rather than parsing
LLM free text.

---

### Case 3: Q13 / Q15 — Hedging failure due to partial topical overlap

**Q13 query:** "Upon completing the UTS Master of Information Technology,
what post-study migration pathways are available?"
**Q15 query:** "How many years does the Temporary Graduate Visa (Subclass
485) grant? Is there a difference in post-study work entitlement between
completing a two-year and a three-year master's program?"

**Observed behaviour:** Both queries are designed as out-of-scope (the
knowledge base contains no migration/visa data). The grading mechanism
*failed* to trigger low_confidence on either, returning max_grade in the
0.6-0.8 range instead of the expected ≤0.2.

**Root cause analysis:** Retrieval returned UTS/UNSW chunks containing
keywords semantically adjacent to the query (ACS accreditation, program
duration). The grader (qwen3:4b applying our 6-level scale) assigned high
relevance based on keyword overlap, without recognising that the chunks
did not address the *information need* (migration eligibility / visa rules).

**Significance:** Our grading prompt rules SCOPE_MISMATCH (cap at 0.2 for
University A vs B) and TOPIC_DOMAIN_MISMATCH (cap at 0.2 for clearly
off-topic) do not cover **partial topical overlap** — queries anchored to
a known entity but asking about adjacent domains. A more granular grading
criterion, possibly with explicit "does the chunk answer the question"
verification rather than topic similarity, would address this.

---

### Case 4: Over-triggering on comparative in-scope queries (Q3–Q6)

**Affected queries:** Q3 (UTS vs UNSW key differences), Q4 (English
requirements comparison), Q5 (tuition fee comparison), Q6 (duration
comparison) — all four are in-scope two-source comparison queries.

**Observed behaviour:** All four triggered low_confidence despite the
knowledge base fully covering both sources. The max-grade decision rule
showed individual chunks scoring 1.0, but other chunks in the same retrieval
batch scored 0.0, and in some cases the max-grade fell below the 0.5
threshold within sub-questions.

**Root cause analysis:** Comparison queries trigger multiple retrievals
(one per university); within each retrieval, ~5 chunks are returned, of
which only a subset are topically relevant to the *comparison axis* being
queried. The remaining chunks (e.g. unrelated sections of the same .md
file) lower the per-chunk grade distribution and can cause max-grade
fluctuation.

**Significance:** This is a **trustworthiness false-positive** — the system
hedges when it should be confident. From a user-trust calibration perspective,
this is less harmful than the inverse (false-negative hallucination), but
indicates the threshold and decision rule may need re-tuning for
multi-source synthesis workflows.

---

### Synthesis: The common thread

All four cases share a structural property: **prompt-engineered behaviour
and LLM-as-judge mechanisms are probabilistic, not deterministic, trust
guarantees**. The trustworthiness layer succeeds in shifting the system's
*default* behaviour toward source-grounded, hedged responses (as evidenced
by the quantitative metrics above), but it does not eliminate failure modes
that emerge from the underlying LLM's stochastic nature.

A future architectural iteration would need to combine prompt rules with
hard constraints — e.g. citation propagation through state, post-generation
fact-verification, or constrained decoding — to provide stronger guarantees.
This is discussed further in Section 8 (Future Work) of the project report.

## Notes on Methodology

This evaluation uses **manual trustworthiness metrics tailored to the research thesis**, in lieu of standard RAGAS metrics (which were incompatible with the project's langchain 1.4 dependency). The metrics chosen — citation recall, hedging rate, tier coverage, multi-source synthesis — directly correspond to the trustworthiness mechanisms (Phases A–D) implemented in the enhancement layer.

Faithfulness was not computed automatically; instead, a qualitative case study analysis on 3–4 representative questions is provided in the project report Section 6.
