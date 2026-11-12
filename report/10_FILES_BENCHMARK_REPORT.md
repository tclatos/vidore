# ViDoRe v3 Industrial: 10-File Multi-Document Benchmark & Trajectory Analysis Report

**Date**: 2026-11-12  
**Dataset**: [ViDoRe v3 Industrial](https://huggingface.co/datasets/vidore/vidore_v3_industrial) (`vidore/vidore_v3_industrial`)  
**Stack**: [genai-tk](https://github.com/tclatos/genai-tk) + [genai-graph](https://github.com/tclatos/genai-graph) (Ladybug DB + Mistral OCR + DecisionRAG)  
**Corpus Scope**: 10 Technical Manuals & Checklists (474 pages, 818 sections, 97 images)  
**Evaluator**: `DeepSeek-V4-Pro-0813@openrouter` with strict domain grading rubric  

---

## 1. Executive Summary

Following the initial single-file pilot, this benchmark evaluates the **Document Graph** and **DecisionRAG (Decision-Model Navigation)** architecture at multi-document scale across **10 technical orders and maintenance manuals** (474 pages) from the ViDoRe v3 Industrial dataset.

All recommendations from the pilot report were implemented, including:
1. **Mistral OCR Batch Ingestion**: Successfully converted 10 PDF manuals in parallel using Mistral Batch API (`use_batch_api: true`).
2. **Updated State-of-the-Art Model Pipeline**: Upgraded outline extraction to `deepseek-v4.1-flash-1017(none)@openrouter` and visual descriptions to `gemini-3.5-flash-lite@openrouter`.
3. **Domain Routing Context**: Created and wired `skills/custom/vidore-industrial-qa/decision-routing.md` to guide System-1 branch scoring at L1 (document level) and L2 (section level).
4. **Buffer Pool & Concurrency Hardening**: Sized Ladybug buffer pool to 8GB and resolved an upstream `langchain_openai` connection-pool reuse bug (`_cached_async_httpx_client.cache_clear()`).
5. **CommonMark Tokenizer Resilience**: Patched a parser vulnerability where OCR number grids corrupted CommonMark list states, expanding graph fidelity from 416 to **818 non-overlapping sections**.

Across a diverse test suite of 13 questions representing all 10 documents, **DecisionRAG achieved 92.3% strict accuracy (12/13 correct, 1 partial, 0 incorrect, 96.2% weighted accuracy)**, dramatically outperforming the **Baseline Deep Agent at 61.5% strict accuracy (8/13 correct, 3 partial, 2 incorrect)**.

DecisionRAG eliminated 80% of retrieval errors, reduced average tool calls from 8.77 to 6.08 per turn, and saved 104,277 prompt tokens, at a negligible navigation cost of **$0.0015 per question**.

---

## 2. Ingested 10-Document Corpus Overview

| Document ID | Pages | Heading Sections | Extracted Images | Subject Matter & Technical Scope |
|---|---|---|---|---|
| **`AFD-091005-062`** | 2 | 3 | 0 | TO 00-25-232: Control & use of insulating rubber matting for high-voltage aviation zones. |
| **`TO_34-1-3`** | 12 | 25 | 0 | Commercial shop machinery, machine tool maintenance, physical hazard color coding (Safety Yellow). |
| **`AFD-091005-056`** | 18 | 28 | 0 | TO 00-25-172CL-2: Concurrent servicing checklist for commercial contract cargo aircraft (LOGAIR/QUICKTRANS). |
| **`TO_00-25-172CL-1`** | 28 | 48 | 0 | Support equipment & personnel locations for concurrent refueling of Boeing & passenger aircraft. |
| **`TO_00-25-260`** | 46 | 85 | 19 | Item Unique Identification (IUID / UID) asset marking & tracking of legacy USAF assets (Laser DPM). |
| **`TO_00-25-245_1`** | 50 | 101 | 20 | Technical manual quality program, deficiency reporting (AFTO Form 22), safety equipment in FSG 4200. |
| **`TO_00-25-172CL-3`** | 68 | 87 | 29 | Hot refueling checklist for U.S. Navy aircraft at USAF bases (carrier aircraft, tactical fighters). |
| **`TO_00-25-203`** | 76 | 148 | 29 | Contamination control standards & clean room laminar airflow specifications for aerospace facilities. |
| **`TO_00-25-172CL-5`** | 82 | 141 | 0 | R-12 hydrant servicing vehicle operations, defueling procedures, rapid defueling separation rules. |
| **`TO_00-25-172CL-4`** | 92 | 152 | 0 | Hot refueling & servicing checklist for tactical airframes, shelter vs. open-air safety perimeters. |
| **Corpus Total** | **474** | **818** | **97** | **10 manuals covering flightline servicing, safety perimeters, UID marking, and clean room facilities.** |

---

## 3. Head-to-Head Benchmark Evaluation Results

Evaluated across 13 diverse questions selected to span all 10 documents, covering question formats (question, instruction, keyword) and reasoning types (open-ended, boolean, enumerative, numerical, compare-contrast, extractive).

### Metric Comparison

| Metric | Baseline Deep Agent (`default`) | DecisionRAG Navigator (`decision_fast`) | Improvement / Advantage |
|---|---|---|---|
| **Total Questions Evaluated** | 13 | 13 | Evaluated across 10 distinct manuals |
| **Strict Accuracy** | 61.5% (8/13) | **92.3% (12/13)** | **+30.8% accuracy gain** |
| **Weighted Accuracy (corr + 0.5*part)** | 73.1% | **96.2%** | **+23.1% weighted gain** |
| **Incorrect Answers** | 2 (15.4%) | **0 (0.0%)** | **Zero incorrect answers** |
| **Groundedness Rate** | 100.0% | **100.0%** | 100% adherence to manual citations |
| **Numeric Match Rate** | 80.0% (4/5) | **80.0% (4/5)** | High numerical precision |
| **Average Tool Calls / Turn** | 8.77 | **6.08** | **-30.7% fewer tool calls** |
| **Total Input Tokens** | 1,185,041 | **1,080,764** | **-104,277 prompt tokens (-8.8%)** |
| **Total Output Tokens** | 41,253 | **39,894** | **-1,359 completion tokens** |
| **Decision Model Invocations** | 0 | 157 calls (avg ~12/question) | Fully automated branch scoring |
| **Decision Model Tokens** | 0 | 575,953 tokens | System-1 zero generated tokens |
| **Total Decision Model Cost** | $0.00 | **$0.0204** | **~$0.0015 / question** |
| **Retrieval / Lookup Errors** | 5 | **1** | **-80% retrieval errors** |
| **Halted / Empty Responses** | 0 | **0** | Perfect stability |

---

## 4. Question-by-Question Diagnostic Breakdown

| Question ID | Target Document | Query Summary & Key Entity | Baseline (`default`) | DecisionRAG (`decision_fast`) | Analysis & Root Cause |
|---|---|---|:---:|:---:|---|
| `vidore_ind_1` | `TO_00-25-172CL-4` | Emergency shutdown action sequence | Partial | **Correct** | Baseline missed the main tank valve closure step. DecisionRAG retrieved the full sequence. |
| `vidore_ind_6` | `AFD-091005-056` | Technical diagram revision update symbols | **Correct** | **Correct** | Both correctly cited vertical margin lines, shaded areas, and pointing hands. |
| `vidore_ind_8` | `TO_00-25-203` | Airflow type for aerospace clean rooms | **Correct** | **Correct** | Both accurately identified laminar airflow and cited contamination control standards. |
| `vidore_ind_9` | `TO_00-25-172CL-3` | Hot refueling safety protocols for Navy aircraft | Partial | **Correct** | Baseline omitted radar standoff (300 ft). DecisionRAG included all limits (55 PSI, 300 ft, 50 ft). |
| `vidore_ind_13` | `TO_00-25-172CL-1` | ARFF fire vehicle requirement for JP-4/Jet B | **Correct** | **Correct** | Both confirmed the conditional requirement when passengers are present on board. |
| `vidore_ind_18` | `AFD-091005-056` | GPU positioning vs. fuel truck placement | **Correct** | **Correct** | Both extracted the 50 ft upwind / 45° nose rule and APU exhaust standoff. |
| `vidore_ind_26` | `TO_00-25-172CL-1` | Count of Boeing models covered in protocol | **Incorrect** | **Correct** | Baseline counted only 5 models. DecisionRAG retrieved full table and enumerated all 7 (B-707 to B-777). |
| `vidore_ind_27` | `TO_00-25-172CL-4` | Safety zone requirements: shelter vs. open-air | Partial | Partial | Both captured engine run-time limits and FSSZ rules; missed secondary spotter/chock details. |
| `vidore_ind_33` | `AFD-091005-062` | Standards regulating high-voltage matting | **Correct** | **Correct** | Both cited MIL-M-15562 and AFOSH 91-50 verbatim. |
| `vidore_ind_37` | `TO_00-25-172CL-5` | Rapid defueling wing-tip separation with fire truck | **Correct** | **Correct** | Both extracted the exact reduced separation distance of **35 feet**. |
| `vidore_ind_71` | `AFD-091005-056` | Factors affecting servicing safety zones | **Correct** | **Correct** | Both identified aircraft type, loaders/open-flame heaters, and concurrent servicing operations. |
| `vidore_ind_91` | `TO_00-25-260` | Durable UID asset marking technique | **Incorrect** | **Correct** | Baseline guessed anodized aluminum plates. DecisionRAG scored and retrieved **Laser DPM**. |
| `vidore_ind_116` | `TO_34-1-3` | Color representing physical hazards | **Correct** | **Correct** | Both identified **Safety Yellow** and outlined the full OSHA/AFMAN color code scheme. |

---

## 5. Architectural & Implementation Insights

### 5.1 Why DecisionRAG Outperforms LLM Tool-Calling on Multi-Manual Corpora
In single-document corpora, manual table-of-contents navigation is manageable because candidate sections are few. In a 10-document corpus with 818 sections across multiple overlapping checklist variants (`CL-1` through `CL-5`), an LLM agent navigating with tool calls suffers from:
1. **Manual Disambiguation Flailing**: The agent repeatedly calls `list_documents`, `get_document_toc`, and `search_sections` across multiple manuals, often stopping on an incomplete table in the wrong checklist variant (e.g. `vidore_ind_26` and `vidore_ind_91`).
2. **Context Window Pollution**: Successive tool call outputs consume context, causing the agent to summarize early or miss subsequent rows.
3. **DecisionRAG Advantage**: The Decision Model evaluates all 10 candidate manuals simultaneously in a single L1 joint score pass, selects the top 4 candidates (`beam_width: 4`), and scores candidate sections in parallel (L2). The synthesis agent receives an all-or-nothing **Evidence Pack** with exact verbatim sections pre-assembled, requiring only direct reading and synthesis.

### 5.2 Critical Engineering Fixes Applied
1. **Async HTTP Client Event Loop Leak**:
   - `langchain_openai` caches `_cached_async_httpx_client` across instances via `@lru_cache`. In multi-task workflows where `asyncio.run()` creates and closes distinct event loops, subsequent tasks reused a client bound to a closed loop, throwing `RuntimeError: Event loop is closed`.
   - **Fix**: Added explicit `_client_utils._cached_async_httpx_client.cache_clear()` calls in `flows.py` before and after each question execution and grading task.
2. **CommonMark List Tokenizer Vulnerability**:
   - Technical orders frequently feature page-number rulers or OCR sequence grids (e.g. ` 1.   2.   3. ... 1000.`). CommonMark parsed these as deeply nested ordered lists, halting block-level tokenization and swallowing all subsequent headings.
   - **Fix**: Added an automated pre-tokenization sanitization pass in `tree_parser.py` that replaces OCR number sequences with non-structural comments, preserving exact line numbers while recovering 100% of document headings.
3. **Recursion Limit Pairing**:
   - Raised `recursion_limit` from 64 to 160 in `config/agents.yaml` to ensure LangGraph never prematurely truncates complex multi-step synthesis trajectories before `WrapUpMiddleware` forces a final answer.

---

## 6. Recommendations for Scaling to the Full 27-Manual Corpus

With 10 manuals (474 pages) fully validated at **96.2% weighted accuracy**, the benchmark is ready to scale to the remaining 17 manuals (4,770 pages, 283 total questions):

1. **Full Corpus Mistral OCR Pre-pass**:
   - Several remaining manuals exceed 300 pages (e.g. `TO_00-25-259` with 892 pages, `TO_32-1-101` with 490 pages, `TO_1-1-691` with 410 pages).
   - Execute a batch pre-conversion:
     ```bash
     uv run cli bench run --step fetch
     uv run cli bench run --step build
     ```
   - Mistral OCR's batch API processes 100-page batches asynchronously with exponential retry backoff.
2. **Ladybug Buffer Pool Allocation**:
   - The full 27 manuals will generate ~20,000+ sections and vector chunks. Retain `LADYBUG_BUFFER_POOL_SIZE=8GB` (or allocate 12GB on high-RAM instances) to keep BM25 tables and HNSW vectors in memory.
3. **Maintain Sequential or Dual Concurrency**:
   - Keep `runner.concurrency: 1` or `2`. Given that each question executes in 15–25 seconds, running 283 questions sequentially takes ~70 minutes, which avoids thread-pool connection thrashing and buffer-pool locks.
4. **Active Profile Selection**:
   - Use `decision_fast` as the primary benchmark profile. Its 92.3% strict accuracy and $0.0015/question navigation cost make it the optimal configuration for evaluating ViDoRe v3 Industrial at scale.
