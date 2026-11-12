# Pilot Evaluation & Trajectory Analysis Report: ViDoRe v3 Industrial

**Date**: 2026-11-12  
**Dataset**: [ViDoRe v3 Industrial](https://huggingface.co/datasets/vidore/vidore_v3_industrial) (`vidore/vidore_v3_industrial`)  
**Stack**: [genai-tk](https://github.com/tclatos/genai-tk) + [genai-graph](https://github.com/tclatos/genai-graph) (Ladybug DB + Mistral OCR + DecisionRAG)  
**Target Document Evaluated**: `AFD-091005-056.pdf` (*TO 00-25-172CL-2: Checklist for Concurrent Servicing of Commercial Contract Cargo Aircraft LOGAIR and QUICKTRANS*, 18 pages)  

---

## 1. Executive Summary

This pilot benchmark evaluates the Document Graph architecture and Decision-Model Navigation (**DecisionRAG**) on the newly released **ViDoRe v3 Industrial** dataset. ViDoRe v3 focuses on visual and document retrieval across complex real-world enterprise publications, with the industrial split comprising 27 USAF Technical Orders and maintenance checklists (5,244 pages total) accompanied by human-verified ground-truth questions and bounding-box page annotations.

In this pilot run, we established the new benchmark repository `vidore`, implemented the dataset adapter, ingested the target aircraft checklist using Mistral OCR into an embedded Ladybug Document Graph, and performed a head-to-head comparison between:
1. **Baseline Deep Agent (`default`)**: `glm_5.3_flash@openrouter` with an LLM-in-the-loop navigation loop (`list_documents`, `get_document_toc`, `get_section_content`).
2. **DecisionRAG Navigator (`decision_fast`)**: System-1 Decision Model (`decision_model: accurate` / `jev@openrouter`) performing deterministic zero-generation tree navigation, paired with a `glm_5.3_flash` synthesis agent.

Both profiles achieved **100% strict correctness and 100% groundedness** on the evaluated benchmark questions. Crucially, DecisionRAG demonstrated a **32.1% reduction in input tokens** and a **27.6% reduction in output tokens** with an average navigation cost of just **$0.0001 per question**.

---

## 2. Evaluation Results Summary

Three representative benchmark questions mapped to `AFD-091005-056` were evaluated:
- **`vidore_ind_6`**: Visual indicators in technical diagrams for revision updates (outer margin lines, shaded/screened areas, pointing hands).
- **`vidore_ind_18`**: Aircraft ground equipment positioning (GPU 50 ft min upwind / within 45° of nose vs. fuel truck 50 ft from APU exhaust).
- **`vidore_ind_71`**: Factors affecting aircraft servicing safety zones (aircraft type, loaders/open-flame heaters, concurrent operations).

### Performance & Efficiency Metrics

| Metric | Baseline Deep Agent (`default`) | DecisionRAG Navigator (`decision_fast`) | Delta / Advantage |
|---|---|---|---|
| **Total Questions Evaluated** | 3 | 3 | - |
| **Strict Accuracy** | **100.0% (3/3)** | **100.0% (3/3)** | Parity (100%) |
| **Numeric Precision Match** | **100.0% (1/1)** | **100.0% (1/1)** | Parity (100%) |
| **Groundedness Rate** | **100.0%** | **100.0%** | Parity (100%) |
| **Average Tool Calls / Turn** | 4.67 | **4.00** | **-14.3% fewer tool calls** |
| **Total Input Tokens** | 122,911 | **83,408** | **-32.1% (-39,503 tokens)** |
| **Total Output Tokens** | 8,033 | **5,814** | **-27.6% (-2,219 tokens)** |
| **Decision Model Calls** | 0 | 6 calls (avg 2/question) | - |
| **Decision Model Tokens** | 0 | 2,849 tokens | - |
| **Decision Model Cost** | $0.00 | **$0.000103** (~$0.00003/q) | Negligible |
| **Agent LLM** | `glm_5.3_flash@openrouter` | `glm_5.3_flash@openrouter` | Identical |
| **Judge LLM** | `DeepSeek-V4-Pro-0813@openrouter` | `DeepSeek-V4-Pro-0813@openrouter` | Identical |

---

## 3. Trajectory & Execution Trace Analysis

We analyzed the execution traces recorded via NeMo Relay into the local ATOF trajectory store (`data/trajectories/`).

### Case Study: Question `vidore_ind_71` ("factors affecting aircraft servicing safety zones")

#### Baseline Trajectory (`01a1cd27-00bb-7271-b22e-952630e5ba73`):
- **Turn 1 (User)**: Receives question.
- **Turn 2 (LLM)**: Reads domain skill (`vidore-industrial-qa/SKILL.md`) and calls `list_documents()`.
- **Turn 3 (LLM)**: Receives document listing, calls `get_document_toc(document_id='file_b1070bb4d8b79eee', max_level=2)`.
- **Turn 4 (LLM)**: Inspects TOC sections, calls `get_section_content` for candidate sections.
- **Turn 5 (LLM)**: Synthesizes final answer (2,655 output tokens).
- **Execution Cost**: 4 LLM turns, 38,948 prompt tokens.

#### DecisionRAG Trajectory (`01a1cd28-99ce-71a1-a7c6-7115bbf87731`):
- **Turn 1 (User)**: Receives question.
- **Turn 2 (LLM)**: Reads domain skill, immediately invokes `navigate_folder(query='factors affecting aircraft servicing safety zones')`.
  - The Decision Model evaluated candidate documents (L1) and candidate sections (L2) in parallel without generating tokens.
  - An **Evidence Pack** was rendered directly into the tool output, containing high-scoring sections with verbatim text under the 10,000-character budget.
- **Turn 3 (LLM)**: Reviews the evidence pack and requests one additional specific subsection (`file_b1070bb4d8b79eee::3`).
- **Turn 4 (LLM)**: Emits comprehensive final answer (2,642 output tokens).
- **Execution Cost**: 3 LLM turns, 33,440 prompt tokens.

### Key Trajectory Insights
1. **Zero-Token Navigation**: The decision model collapsed the separate `list_documents` and `get_document_toc` phases into a single tool invocation, eliminating intermediate LLM round-trips.
2. **Pack Budget Stability**: Setting `pack_char_budget: 10000` (well below `ObservationTruncationMiddleware.max_chars: 16000`) prevented oversized tool outputs, ensuring that the agent did not get trapped in defensive `read_file` loops.
3. **Synthesis Consistency**: With relevant text pre-assembled in the evidence pack, the synthesis agent adhered strictly to checklist cautions, quoting exact distances (50 ft GPU standoff, 25 ft wing vent standoff, 10 ft radio ban) without hallucinations.

---

## 4. Recommendations Before Scaling to the Full Corpus

Before launching a full-scale run across all 27 technical manuals (5,244 pages) and 283 English questions, the following improvements are recommended:

### 4.1 Ingestion & OCR Scale
1. **Handling Very Large Documents**:
   - Several manuals in the industrial corpus are large (e.g., `TO_00-25-259` with 892 pages, `TO_32-1-101` with 490 pages, `TO_1-1-691` with 410 pages).
   - Use Mistral OCR's batch mode (`use_batch_api: true`) and run document conversion as a distributed pre-pass (`cli bench run --step build`) before initiating agent evaluation.
2. **Lossless Table & Diagram Extraction**:
   - Ensure `include_image_base64: true` and `table_format: html` are preserved so complex wiring diagrams, layout figures, and multipart checklists remain readable in the markdown trees.

### 4.2 Document Graph & Database Capacity
1. **Buffer Pool Sizing**:
   - Ingesting all 5,244 pages will yield ~20,000+ sections and vector chunks.
   - Configure `LADYBUG_BUFFER_POOL_SIZE=8GB` to provide ample headroom for HNSW indexes, BM25 tables, and concurrent multi-question reader queries.
2. **Runner Concurrency**:
   - Set `runner.concurrency: 2` or `3` (not higher) to prevent resource contention on local SQLite/Ladybug database connections and avoid memory spikes during concurrent LLM streaming.

### 4.3 DecisionRAG Tuning for Multi-Document Retrieval
1. **Domain Routing Context**:
   - In a single-document setting, L1 document selection is trivial. In a 27-document corpus, queries often reference specific aircraft designations (e.g. C-130, KC-135, B-727) or specific operational domains (fuel servicing, cargo loading, corrosion control).
   - Author a dedicated `decision-routing.md` in `skills/custom/vidore-industrial-qa/` that maps technical order numbers (e.g. `TO 00-25-172` vs `TO 1-1-691`) to their primary aircraft systems. Pass this file via `domain_context_file` in `config/agents.yaml`.
2. **Multi-Document Beam Width**:
   - For multi-document questions (approx. 8% of queries span >1 manual), set `beam_width: 3` and `top_r_sections: 8` to ensure relevant sections from multiple manuals enter the evidence pack.

### 4.4 Automated Multi-Run Evaluation
- Add a dedicated Justfile recipe (`just bench-full`) to execute the pipeline with automated logging and report generation:
  ```bash
  # Pre-fetch & build entire corpus
  uv run cli bench run --step fetch
  uv run cli bench run --step build
  # Run baseline and DecisionRAG profiles in parallel or sequence
  uv run cli bench run -p default
  uv run cli bench run -p decision_fast
  # Generate comparison report
  uv run cli bench report -p default
  uv run cli bench report -p decision_fast
  ```
