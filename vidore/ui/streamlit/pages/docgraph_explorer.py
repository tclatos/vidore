"""Streamlit page: ViDoRe Technical Orders Document & PDF Explorer.

Visualizes USAF Technical Orders as ingested into the Document Graph:
- Document outlines and metadata
- Section-by-section inspection with rendered Markdown, figures, and tables
- Original USAF source PDF comparison via native st.pdf
"""

from __future__ import annotations

import os
from pathlib import Path

import streamlit as st
from genai_graph.ui.streamlit.components.docgraph_inspector import render_docgraph_inspector
from genai_graph.ui.streamlit.components.docgraph_view import get_docgraph_backend


def main() -> None:
    """Render the Document & PDF Explorer page."""
    st.markdown("## 📑 Technical Orders & Document Graph Explorer")
    st.caption("Inspect USAF Technical Orders, section hierarchies, figures, and original PDF manuals.")

    # Locate database
    default_db = "data/kg/vidore.db"
    db_path = os.getenv("DOCGRAPH_DB_PATH", default_db)

    p_db = Path(db_path)
    if not p_db.exists():
        st.error(f"Document Graph database not found at `{p_db.resolve()}`. Run `cli docgraph build` first.")
        return

    # Connect backend
    try:
        backend = get_docgraph_backend(str(p_db.resolve()))
    except Exception as exc:
        st.error(f"Failed to connect to Document Graph database at `{p_db}`: {exc}")
        return

    pdf_dirs = [
        Path.cwd() / "data" / "pdfs",
        Path.cwd() / "pdfs",
    ]

    render_docgraph_inspector(
        backend=backend,
        db_path=str(p_db.resolve()),
        pdf_dirs=pdf_dirs,
        default_layout="tabbed",
    )


try:
    _ = st.session_state
    main()
except (AttributeError, RuntimeError, Exception):
    pass
