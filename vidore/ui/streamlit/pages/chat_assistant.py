"""Streamlit page: ViDoRe Industrial Technical Order QA Chat Assistant.

Interactive chat interface powered by the DecisionRAG Navigator agent:
- Answers USAF Technical Order and flightline checklist questions
- Real-time execution trace display (decision model calls, evidence packs, tools)
- Dynamic LLM model switching via llm_selector_widget
- Benchmark sample questions for quick one-click testing
"""

from __future__ import annotations

import uuid
from typing import Any

import streamlit as st
from genai_tk.agents.harness import create_harness
from genai_tk.agents.harness.base import BaseHarness
from genai_tk.ui.config.chat import ChatDisplayConfig
from genai_tk.ui.streamlit.components.agent_layout import (
    PANEL_HEIGHT,
    render_agent_sidebar,
)
from genai_tk.ui.streamlit.components.harness_workbench import (
    render_artifact,
    render_artifact_gallery,
    render_trace_panel,
    stream_harness_turn,
)
from genai_tk.ui.streamlit.components.message_renderer import render_message_with_mermaid
from streamlit import session_state as sss

_chat_cfg = ChatDisplayConfig.from_config("ui.display.chat")
CHAT_HEIGHT = _chat_cfg.chat_height or PANEL_HEIGHT
TRACE_HEIGHT = _chat_cfg.trace_height or PANEL_HEIGHT

AGENT_PROFILE_KEY = "decision"

SAMPLE_QUESTIONS = [
    "Explain the sequence of actions required to execute an emergency shutdown during aircraft fuel servicing.",
    "What is the minimum fire hazard safety distance required during liquid oxygen (LOX) servicing?",
    "What specific personal protective equipment (PPE) must personnel wear when servicing liquid oxygen?",
    "Under what temperature or weather conditions are wheel chocks required to be installed on aircraft?",
    "What visual indicator or symbol marks revised diagrams or procedures in USAF Technical Orders?",
]


def _init_session_state() -> None:
    """Initialize chat session state."""
    defaults: dict[str, Any] = {
        "vidore_messages": [],
        "vidore_harness": None,
        "vidore_thread_id": None,
        "vidore_trace_steps": [],
        "vidore_artifacts": [],
        "vidore_selected_artifact": None,
        "vidore_error": None,
    }
    for k, v in defaults.items():
        if k not in sss:
            sss[k] = v


def _clear_history() -> None:
    """Reset chat history and traces."""
    sss.vidore_messages = []
    sss.vidore_thread_id = None
    sss.vidore_trace_steps = []
    sss.vidore_artifacts = []
    sss.vidore_selected_artifact = None
    sss.vidore_harness = None


def _get_harness() -> BaseHarness:
    """Get or instantiate the DecisionRAG harness."""
    if sss.vidore_harness is not None:
        return sss.vidore_harness

    harness = create_harness(
        AGENT_PROFILE_KEY,
        force_memory_checkpointer=True,
    )
    sss.vidore_harness = harness
    return harness


def main() -> None:
    """Main entry point for the Industrial QA Chat assistant."""
    _init_session_state()

    st.markdown("## 💬 ViDoRe Industrial QA Assistant")
    st.caption("Ask questions about USAF Technical Orders, ground servicing checklists, and safety procedures.")

    # ── Sidebar ───────────────────────────────────────────────────────────
    with st.sidebar:
        st.subheader("Agent Configuration")
        st.markdown("**Profile:** `decision` (DecisionRAG Navigator)")
        st.caption("Navigates Document Graph via System-1 decision models + evidence packs.")

        # Quick sample questions
        with st.expander("💡 Sample Benchmark Questions", expanded=True):
            for idx, q_text in enumerate(SAMPLE_QUESTIONS):
                if st.button(f"#{idx + 1}: {q_text[:40]}...", key=f"q_btn_{idx}", use_container_width=True):
                    sss.user_prompt_input = q_text

        if st.button("🗑️ Clear Chat History", use_container_width=True):
            _clear_history()
            st.rerun()

        st.divider()
        # LLM model switcher (Provider -> Lab -> Model)
        render_agent_sidebar("")

    if sss.vidore_error:
        st.error(sss.vidore_error)
        if st.button("Dismiss Error"):
            sss.vidore_error = None
            st.rerun()

    # ── Two-Panel Layout: Trace on Left | Chat on Right ───────────────────
    col_trace, col_main = st.columns([2, 3], gap="medium")

    with col_trace:
        st.subheader("🔍 Execution Trace")
        with st.container(height=TRACE_HEIGHT, border=True):
            if sss.vidore_trace_steps:
                render_trace_panel(sss.vidore_trace_steps, key_prefix="vidore")
            else:
                st.info("Execution trace and decision model steps will appear here during query processing.")

    with col_main:
        tab_chat, tab_artifact = st.tabs(["💬 Chat", "📄 Evidence & Artifacts"])

        with tab_chat:
            with st.container(height=CHAT_HEIGHT, border=True):
                if not sss.vidore_messages:
                    st.info(
                        "👋 Welcome! I can answer technical questions about military aircraft Technical Orders (TO).\n\n"
                        "Select a sample question from the sidebar or type a question below."
                    )
                for msg in sss.vidore_messages:
                    if msg["role"] == "user":
                        st.chat_message("human").write(msg["content"])
                    else:
                        with st.chat_message("ai"):
                            render_message_with_mermaid(msg["content"], st)

        with tab_artifact:
            with st.container(height=CHAT_HEIGHT, border=True):
                if sss.vidore_selected_artifact:
                    if st.button("← All outputs"):
                        sss.vidore_selected_artifact = None
                        st.rerun()
                    render_artifact(sss.vidore_selected_artifact)
                else:
                    render_artifact_gallery(sss.vidore_artifacts, key_prefix="vidore")

    # ── Chat input ────────────────────────────────────────────────────────
    prefilled = sss.pop("user_prompt_input", None)
    user_input = st.chat_input("Ask a question about the Technical Orders…", key="chat_input")
    active_prompt = user_input or prefilled
    if not active_prompt:
        return
    active_prompt = active_prompt.strip()

    sss.vidore_messages.append({"role": "user", "content": active_prompt})
    sss.vidore_selected_artifact = None

    if not sss.vidore_thread_id:
        sss.vidore_thread_id = uuid.uuid4().hex

    try:
        harness = _get_harness()
    except Exception as exc:
        sss.vidore_error = f"Failed to initialize agent harness: {exc}"
        st.rerun()
        return

    with col_trace:
        with st.status("🤖 Reasoning & Navigating Technical Orders…", expanded=True) as status_widget:
            response_placeholder = st.empty()
            try:
                turn = stream_harness_turn(
                    harness,
                    active_prompt,
                    thread_id=sss.vidore_thread_id,
                    response_placeholder=response_placeholder,
                )
                status_widget.update(label="✅ Answer Complete", state="complete", expanded=False)
            except Exception as exc:
                sss.vidore_error = f"Agent execution error: {exc}"
                status_widget.update(label="❌ Error", state="error")
                st.rerun()
                return

    response_placeholder.empty()

    if not turn.text:
        st.rerun()
        return

    sss.vidore_trace_steps = turn.steps
    sss.vidore_messages.append({"role": "assistant", "content": turn.text})
    tool_artifacts = [tool.artifact for step in turn.steps for tool in step.tools if tool.artifact is not None]
    sss.vidore_artifacts = tool_artifacts + turn.artifacts

    st.rerun()


try:
    _ = st.session_state
    main()
except (AttributeError, RuntimeError, Exception):
    pass
