"""Unit tests for the ViDoRe Streamlit web application pages and configuration."""

from __future__ import annotations

from pathlib import Path

from genai_graph.ui.streamlit.components.docgraph_inspector import find_document_pdf
from genai_tk.config_mgmt.config_mngr import global_config


def test_ui_configuration_registered() -> None:
    """Verify that ui: section is properly registered in global config."""
    cfg = global_config()
    app_name = cfg.get_str("ui.app_name")
    assert "ViDoRe" in app_name

    nav = cfg.get_dict("ui.navigation")
    assert "Corpus & Graph" in nav
    assert "Benchmark Evaluation" in nav
    assert "Interactive Assistant" in nav


def test_vidore_pdf_resolution() -> None:
    """Verify that ViDoRe markdown manuals resolve to their corresponding PDFs."""
    test_cases = [
        "AFD-091005-056_pdf.md",
        "TO_00-25-172CL-1_pdf.md",
        "TO_34-1-3_pdf.md",
    ]
    for md_name in test_cases:
        pdf_path = find_document_pdf(
            doc_filename=md_name,
            doc_path=str(Path("data/markdown_multi") / md_name),
            additional_dirs=[Path("data/pdfs")],
        )
        assert pdf_path is not None, f"Failed to resolve PDF for {md_name}"
        assert pdf_path.is_file()
        assert pdf_path.suffix.lower() == ".pdf"


def test_webapp_page_files_exist() -> None:
    """Verify that all configured webapp page files exist on disk."""
    base = Path("vidore/ui/streamlit")
    assert (base / "app.py").is_file()
    assert (base / "pages" / "docgraph_explorer.py").is_file()
    assert (base / "pages" / "bench_outcomes.py").is_file()
    assert (base / "pages" / "chat_assistant.py").is_file()
