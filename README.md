# ViDoRe v3 Industrial Benchmark (`vidore`)

Benchmarking a **Document Graph + Decision-Model Navigation (DecisionRAG)** stack on the
**ViDoRe v3 Industrial** dataset ([Hugging Face](https://huggingface.co/datasets/vidore/vidore_v3_industrial) · [Collection](https://hf.co/collections/vidore/vidore-benchmark-v3) · [ArXiv:2601.08620](https://arxiv.org/abs/2601.08620)).

The stack — built on [genai-tk](https://github.com/tclatos/genai-tk) and
[genai-graph](https://github.com/tclatos/genai-graph) — turns technical aircraft orders and military maintenance manuals
into a hierarchical `Folder → Document → MarkdownSection` graph in an embedded
Ladybug (Kuzu) database with native BM25 FTS and vector chunking.

Evaluates both:
1. **Autonomous Deep Agent** (`glm_5.3_flash@openrouter`) navigating via graph tools (`get_folder_toc`, `get_document_toc`, `get_section_content`, `search_sections`, `query_image`).
2. **DecisionRAG Navigator** (System-1 Decision Model section selection + synthesis agent) for zero-token deterministic tree navigation.

## Multi-Document Benchmark Results (10 Manuals, 474 Pages, 818 Sections)

Evaluated across 13 diverse questions spanning all 10 ingested manuals, graded by `DeepSeek-V4-Pro-0813` with strict domain rubric:

| Metric | Baseline Deep Agent (`default`) | DecisionRAG Navigator (`decision_fast`) | Improvement / Advantage |
|---|---|---|---|
| **Strict Accuracy** | 61.5% (8/13) | **92.3% (12/13)** | **+30.8% accuracy gain** |
| **Weighted Accuracy (corr + 0.5*part)** | 73.1% | **96.2%** | **+23.1% weighted gain** |
| **Incorrect Answers** | 2 (15.4%) | **0 (0.0%)** | **Zero incorrect answers** |
| **Groundedness Rate** | 100.0% | **100.0%** | 100% manual adherence |
| **Numeric Match Rate** | 80.0% (4/5) | **80.0% (4/5)** | High numerical precision |
| **Average Tool Calls / Turn** | 8.77 | **6.08** | **-30.7% fewer tool calls** |
| **Input Tokens** | 1,185,041 | **1,080,764** | **-104,277 prompt tokens (-8.8%)** |
| **Decision Model Navigation Cost** | $0.00 | **$0.0204** | **~$0.0015 / question** |
| **Retrieval / Lookup Errors** | 5 | **1** | **-80% retrieval errors** |

## Comprehensive Evaluation Results (105 Questions Across 10 Technical Manuals)

Evaluated across all 105 expert-annotated questions mapped to the 10 ingested manuals in the Ladybug Document Graph, graded by `DeepSeek-V4-Pro-0813`.

> **Note on Benchmark Paradigms**: Official ViDoRe v3 MTEB leaderboard metrics measure **page-level retrieval ranking (NDCG@10)** on raw page images (e.g. SOTA `nemo-colembed-3b` achieves **57.0% NDCG@10**, `colqwen2` achieves **49.8% NDCG@10** on Industrial). The evaluation below measures **end-to-end task completion (RAG question answering)** on deterministic procedural steps, safety distances, and technical figures:

| Evaluation Metric | Measured Result (`decision_fast`) | Benchmark Context |
|---|:---:|---|
| **Weighted Accuracy** | **77.1% (81/105)** | `correct + 0.5 * partial` under strict equivalence |
| **Strict Accuracy** | **61.9% (65/105)** | Exact match of all procedural steps & numbers |
| **Partial Accuracy** | **30.5% (32/105)** | Right document/section, missing secondary detail |
| **Incorrect Rate** | **7.6% (8/105)** | Outright contradicted or ungrounded claims |
| **Groundedness Rate** | **92.9% (97/105)** | Citations strictly grounded in technical manual text |
| **Numeric Match Rate** | **75.8% (25/33)** | Exact match on safety distances, PSI limits, counts |
| **Average Tool Calls** | **6.77 / turn** | Compact trajectories driven by Decision Model |
| **System Stability** | **0% failures** | 105/105 questions completed; zero timeouts or loop errors |
| **Total Decision Model Cost** | **$0.1595** | **~$0.0015 per question** (1,179 System-1 calls) |

Detailed reports:
- [Executive Evaluation Report & Industry Baseline Comparison](report/EXECUTIVE_EVALUATION_REPORT.md)
- [10-File Multi-Document Diagnostic Report](report/10_FILES_BENCHMARK_REPORT.md)
- [Initial Pilot Evaluation Report](report/PILOT_REPORT.md)

## Quick Start

```bash
uv sync --extra harnessing
just bench
```

## Running the Benchmark

```bash
# Run specific profile
uv run cli bench run -p default
uv run cli bench run -p decision_fast

# Run on a specific question
uv run cli bench run -q vidore_ind_6

# Filter by document name(s)
uv run cli bench run -d AFD-091005-056,TO_00-25-172CL-1

# View evaluation report
uv run cli bench report -p decision_fast

# Interactive TUI question browser
uv run cli bench tui -p decision_fast

# Interactive Streamlit benchmark dashboard
uv run cli bench web -p decision_fast
```

## Web Application & Interactive Exploration

Launch the multi-page Streamlit webapp:

```bash
just webapp
# or:
uv run streamlit run vidore/ui/streamlit/app.py
```

The webapp provides three dedicated pages:
1. **Document & PDF Explorer** (`docgraph_explorer.py`):
   - Interactive outline and section browser over the 10 USAF Technical Orders in `data/kg/vidore.db`.
   - Single-section focused reading mode with rendered Markdown, resolved embedded images/figures, and tables.
   - Side-by-side **Split Screen** or **Tabbed** comparison with the original source PDF from `data/pdfs/`.
2. **Benchmark Outcomes Dashboard** (`bench_outcomes.py`):
   - Interactive counterpart to `cli bench tui` / `cli bench questions` displaying the 105 evaluated questions.
   - Top-level KPI metrics (Strict Accuracy, Weighted Accuracy, Groundedness, Tool Calls).
   - Multi-criteria filtering by verdict (`✓ Correct`, `~ Partial`, `✗ Incorrect`), manual name, and text query.
   - Detailed side-by-side comparison of gold reference answers, agent responses, LLM judge rationales, and step-by-step tool trajectories & DecisionRAG navigation evidence packs.
3. **Industrial QA Assistant** (`chat_assistant.py`):
   - Interactive chat powered by the `decision` DecisionRAG Navigator.
   - Dynamic model switching via the sidebar LLM selector (`llm_selector_widget`).
   - One-click benchmark sample questions.
   - Live two-panel workbench displaying real-time execution traces (decision model steps, tool calls) alongside streaming answers with manual citations.

