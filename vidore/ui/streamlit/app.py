"""Streamlit entry point for the ViDoRe Benchmark & Industrial QA web application.

Usage:
    just webapp
or:
    uv run streamlit run vidore/ui/streamlit/app.py
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

_here = Path(__file__).resolve().parent
_pages_dir = _here / "pages"

st.set_page_config(
    page_title="ViDoRe Industrial Benchmark",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

pages = {
    "Corpus & Document Graph": [
        st.Page(_pages_dir / "docgraph_explorer.py", title="Document & PDF Explorer", icon="📑", default=True),
    ],
    "Benchmark Evaluation": [
        st.Page(_pages_dir / "bench_outcomes.py", title="Benchmark Outcomes", icon="📊"),
    ],
    "Interactive Assistant": [
        st.Page(_pages_dir / "chat_assistant.py", title="Industrial QA Chat", icon="💬"),
    ],
}

pg = st.navigation(pages, position="top")
pg.run()
