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

# Filter by document name
uv run cli bench run -d AFD-091005-056
```
