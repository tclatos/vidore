"""Streamlit page: ViDoRe v3 Industrial Benchmark Outcomes & Evaluation.

Visualizes evaluated benchmark questions, gold answers, agent responses,
LLM-as-a-judge verdicts, and detailed tool execution traces.
"""

from __future__ import annotations

import os
from pathlib import Path

import streamlit as st
from genai_graph.bench.config import load_bench_profile
from genai_graph.ui.streamlit.components.bench_browser import render_bench_browser


def main() -> None:
    """Render the Benchmark Outcomes dashboard."""
    config_path = os.getenv("BENCH_CONFIG_PATH", "config/bench.yaml")
    cfg_p = Path(config_path)

    default_profile = os.getenv("BENCH_PROFILE", "decision_fast")

    cfg = None
    try:
        cfg = load_bench_profile(profile_name=default_profile, config_path=cfg_p if cfg_p.exists() else None)
    except Exception as exc:
        st.warning(f"Note: Could not preload profile '{default_profile}': {exc}")

    render_bench_browser(
        cfg=cfg,
        profile_name=default_profile,
        config_path=cfg_p if cfg_p.exists() else None,
    )


try:
    _ = st.session_state
    main()
except (AttributeError, RuntimeError, Exception):
    pass
