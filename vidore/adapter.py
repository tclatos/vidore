"""ViDoRe v3 Industrial dataset adapter for military technical orders and maintenance checklists."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow.parquet as pq
from genai_graph.bench.adapters.base import (
    BaseBenchmarkAdapter,
    download_hf_file,
)
from genai_graph.bench.models import BenchQuestion
from loguru import logger

DATASET_ID = "vidore/vidore_v3_industrial"

VIDORE_INDUSTRIAL_RUBRIC = """\
You are a strict-but-fair grader for ViDoRe v3 Industrial, evaluating technical understanding of military aircraft technical orders (TO), servicing checklists, safety zones, and mechanical operations.
Compare the agent's answer to the gold answer using the gold evidence and justification.

Return ONLY a JSON object with exactly these keys:
{
  "correctness": "correct" | "partial" | "incorrect",
  "numeric_match": true | false | null,
  "groundedness": "grounded" | "partial" | "ungrounded",
  "error_category": "missing_ocr_or_visual_chart" | "calculation_or_math_error" | "retrieval_or_lookup_error" | "halted_or_empty_response" | null,
  "rationale": "<one sentence>"
}

Evaluation criteria:
- Technical precision: Check that key technical components, aircraft designations (e.g. C-130, KC-135),
  equipment models (GPU, REO, LVM, CSS), valve types, and procedural steps match the substance of the gold answer.
- Safety & numerical rules: Minimum separation distances (e.g. 50 ft), pressures, temperatures, and tolerances
  must be accurate. Standard rounding differences are acceptable if the meaning is unchanged.
- Procedural & enumerative questions: The agent answer is CORRECT if it includes all critical steps/components
  required by the gold answer. Minor phrasing differences that preserve operational meaning are fully acceptable.
- Superset rule: If the agent provides more relevant procedural or explanatory detail beyond the gold answer,
  it is CORRECT as long as it does not contradict the gold answer or introduce false claims.
- Anti-hallucination / Unanswerable: If the gold answer states information is not specified in the document,
  the agent is CORRECT if it concludes the information is absent.

Tiers:
- "correct": The agent answer accurately captures all substantive facts, safety constraints, components, or procedures.
- "partial": Right direction or partial list of components/steps, but omits key requirements or has minor numerical discrepancy.
- "incorrect": Contradicts gold answer, specifies unsafe/wrong procedures, or cites incorrect technical values.
- "numeric_match": true if numeric values match (allowing rounding); false if numbers disagree; null if non-numeric.
- "groundedness": "grounded" if supported by the manual/checklist context; "ungrounded" if facts appear invented.
- "error_category": When correctness is partial or incorrect:
  * "missing_ocr_or_visual_chart": question requires reading a schematic, wiring diagram, checklist symbol, or layout plot unreadable in text OCR.
  * "calculation_or_math_error": arithmetic or distance conversion error.
  * "retrieval_or_lookup_error": agent searched but referenced the wrong document, section, or checklist item.
  * "halted_or_empty_response": answer is empty, aborted, or a bare status commentary.
"""


def _to_python_type(val: Any) -> Any:
    """Recursively convert numpy/pandas types to native Python primitives."""
    if val is None:
        return None
    if isinstance(val, (list, tuple)):
        return [_to_python_type(x) for x in val]
    if hasattr(val, "tolist"):
        return [_to_python_type(x) for x in val.tolist()]
    if isinstance(val, (pd.Timestamp,)):
        return str(val)
    if hasattr(val, "item"):  # numpy scalar
        return val.item()
    if pd.isna(val):
        return None
    return val


class ViDoReIndustrialAdapter(BaseBenchmarkAdapter):
    """Adapter for vidore/vidore_v3_industrial."""

    name: str = "vidore"

    def _ensure_corpus_index(self, target_dir: Path) -> pd.DataFrame:
        """Load or build lightweight corpus index mapping corpus_id -> doc_id, page_number_in_doc."""
        index_file = target_dir / "corpus_index.parquet"
        if index_file.exists():
            return pd.read_parquet(index_file)

        logger.info("Building lightweight corpus index from Hugging Face {}", DATASET_ID)
        parts: list[pd.DataFrame] = []
        for i in range(5):
            fname = f"corpus/test-{i:05d}-of-00005.parquet"
            p = download_hf_file(repo_id=DATASET_ID, filename=fname, repo_type="dataset")
            table = pq.read_table(p, columns=["corpus_id", "doc_id", "page_number_in_doc"])
            parts.append(table.to_pandas())

        df_corpus = pd.concat(parts, ignore_index=True)
        df_corpus.to_parquet(index_file, index=False)
        logger.info("Cached corpus index ({} pages) to {}", len(df_corpus), index_file)
        return df_corpus

    def load_dataset(self, split: str | None = None, cache_dir: Path | None = None) -> list[BenchQuestion]:
        """Load ViDoRe Industrial English questions and convert to BenchQuestion models."""
        target_dir = cache_dir or (Path.cwd() / "data" / "vidore")
        target_dir.mkdir(parents=True, exist_ok=True)
        questions_cache = target_dir / "questions_en.parquet"

        if questions_cache.exists():
            logger.info("Loading cached ViDoRe Industrial questions from {}", questions_cache)
            df_merged = pd.read_parquet(questions_cache)
        else:
            logger.info("Downloading ViDoRe Industrial queries and qrels from Hugging Face")
            # 1. Queries
            q_path = download_hf_file(
                repo_id=DATASET_ID,
                filename="queries/test-00000-of-00001.parquet",
                repo_type="dataset",
            )
            df_q = pd.read_parquet(q_path)
            # Filter for English queries (283 total)
            df_en = df_q[df_q["language"] == "english"].copy()

            # 2. Qrels
            qrels_path = download_hf_file(
                repo_id=DATASET_ID,
                filename="qrels/test-00000-of-00001.parquet",
                repo_type="dataset",
            )
            df_qrels = pd.read_parquet(qrels_path)

            # 3. Corpus mapping
            df_corpus = self._ensure_corpus_index(target_dir)

            # Join qrels with corpus
            qrels_with_doc = df_qrels.merge(df_corpus, on="corpus_id", how="left")

            # Group documents and evidence pages by query_id
            doc_mapping = (
                qrels_with_doc.groupby("query_id")
                .agg(
                    {
                        "doc_id": lambda s: list(dict.fromkeys(s.dropna())),
                        "page_number_in_doc": list,
                        "content_type": lambda s: list({item for sublist in s.dropna() for item in sublist}),
                    }
                )
                .reset_index()
            )

            df_merged = df_en.merge(doc_mapping, on="query_id", how="left")
            df_merged.to_parquet(questions_cache, index=False)
            logger.info("Cached {} English questions to {}", len(df_merged), questions_cache)

        questions: list[BenchQuestion] = []
        for _, row in df_merged.iterrows():
            q_num = int(row["query_id"])
            q_id = f"vidore_ind_{q_num}"
            raw_docs = _to_python_type(row.get("doc_id"))
            if isinstance(raw_docs, list) and len(raw_docs) > 0:
                doc_names = [str(d) for d in raw_docs]
            elif isinstance(raw_docs, str):
                doc_names = [raw_docs]
            else:
                doc_names = ["unknown"]

            primary_doc = doc_names[0]
            question_text = str(row.get("query", ""))
            gold_answer = str(row.get("answer", ""))

            raw_pages = _to_python_type(row.get("page_number_in_doc")) or []
            pages = raw_pages if isinstance(raw_pages, list) else [raw_pages]
            evidence: list[str] = [f"{primary_doc} p.{p}" for p in pages[:10]]

            metadata: dict[str, Any] = {
                "query_id": q_num,
                "language": _to_python_type(row.get("language")),
                "query_types": _to_python_type(row.get("query_types")),
                "query_format": _to_python_type(row.get("query_format")),
                "content_type": _to_python_type(row.get("content_type")),
                "raw_answers": _to_python_type(row.get("raw_answers")),
                "source_type": _to_python_type(row.get("source_type")),
                "doc_names": doc_names,
            }

            questions.append(
                BenchQuestion(
                    id=q_id,
                    doc_name=primary_doc,
                    doc_names=doc_names,
                    question=question_text,
                    gold_answer=gold_answer,
                    evidence=evidence,
                    justification=None,
                    metadata=metadata,
                )
            )

        return questions

    def fetch_document(self, doc_name: str, output_dir: Path) -> Path:
        """Download raw technical order PDF from Hugging Face."""
        output_dir.mkdir(parents=True, exist_ok=True)
        norm_name = self.resolve_doc_name(doc_name)
        target = output_dir / f"{norm_name}.pdf"
        if target.exists() and target.stat().st_size > 0:
            return target

        pdf_filename = f"{norm_name}.pdf"
        logger.info("Downloading {} from {}/pdfs/...", pdf_filename, DATASET_ID)
        try:
            downloaded = download_hf_file(
                repo_id=DATASET_ID,
                filename=f"pdfs/{pdf_filename}",
                repo_type="dataset",
                output_dir=output_dir,
            )
            return downloaded
        except Exception as exc:
            logger.warning("Could not fetch PDF from HF for {}: {}. Creating placeholder.", norm_name, exc)
            target.write_text(f"Placeholder for {norm_name}", encoding="utf-8")
            return target

    def get_judge_rubric(self) -> str:
        return VIDORE_INDUSTRIAL_RUBRIC
