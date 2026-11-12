"""Unit tests for ViDoRe v3 Industrial adapter and grading rubric."""

from __future__ import annotations

import json
from pathlib import Path

from genai_graph.bench.judge import _parse_judge_json
from genai_graph.bench.models import JudgeVerdict

from vidore.adapter import ViDoReIndustrialAdapter, _to_python_type


def test_adapter_initialization():
    adapter = ViDoReIndustrialAdapter()
    assert adapter.name == "vidore"
    assert "technical orders" in adapter.get_judge_rubric().lower()
    assert adapter.resolve_doc_name("AFD-091005-056.pdf") == "AFD-091005-056"


def test_to_python_type_primitives():
    assert _to_python_type(None) is None
    assert _to_python_type([1, 2, "test"]) == [1, 2, "test"]
    assert _to_python_type({"a": 1}) == {"a": 1}


def test_parse_verdict_vidore_correct():
    raw_json = json.dumps(
        {
            "correctness": "correct",
            "numeric_match": True,
            "groundedness": "grounded",
            "error_category": None,
            "rationale": "GPU placement distance 50 ft matches gold answer and TO 00-25-172CL-2.",
        }
    )
    data = _parse_judge_json(raw_json)
    verdict = JudgeVerdict.model_validate(data)
    assert verdict.correctness == "correct"
    assert verdict.numeric_match is True
    assert verdict.groundedness == "grounded"
    assert verdict.error_category is None


def test_parse_verdict_vidore_lookup_error():
    raw_json = json.dumps(
        {
            "correctness": "incorrect",
            "numeric_match": False,
            "groundedness": "ungrounded",
            "error_category": "retrieval_or_lookup_error",
            "rationale": "Agent looked in Chapter 2 instead of Chapter 1 concurrent servicing checklist.",
        }
    )
    data = _parse_judge_json(raw_json)
    verdict = JudgeVerdict.model_validate(data)
    assert verdict.correctness == "incorrect"
    assert verdict.error_category == "retrieval_or_lookup_error"


def test_questions_cached():
    cache_file = Path("data/vidore/questions_en.parquet")
    if cache_file.exists():
        adapter = ViDoReIndustrialAdapter()
        questions = adapter.load_dataset()
        assert len(questions) == 283
        assert all(q.id.startswith("vidore_ind_") for q in questions)
