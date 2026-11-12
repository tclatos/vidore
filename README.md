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

Detailed reports:
- [10-File Multi-Document Benchmark Report](report/10_FILES_BENCHMARK_REPORT.md)
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
```
