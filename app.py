import streamlit as st
import time
from agents import (
    build_reader_agent,
    build_search_agents,
    writer_chain,
    critic_chain,
)

# ─────────────────────────────────────────────
#  Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Research Intelligence System",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
#  Custom CSS  – dark editorial / intelligence-brief aesthetic
# ─────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=IBM+Plex+Mono:wght@400;500&family=Lora:ital,wght@0,400;0,500;1,400&display=swap');

    /* ── Base ── */
    html, body, [class*="css"] {
        font-family: 'Lora', Georgia, serif;
        background-color: #0b0c10;
        color: #e8e0d0;
    }
    .stApp { background-color: #0b0c10; }

    /* ── Hide Streamlit chrome ── */
    #MainMenu, footer, header { visibility: hidden; }

    /* ── Hero header ── */
    .hero {
        padding: 3.5rem 0 2rem 0;
        text-align: center;
        position: relative;
    }
    .hero-eyebrow {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.72rem;
        letter-spacing: 0.32em;
        color: #c8a96e;
        text-transform: uppercase;
        margin-bottom: 0.9rem;
    }
    .hero-title {
        font-family: 'Syne', sans-serif;
        font-size: clamp(2.4rem, 5vw, 4rem);
        font-weight: 800;
        line-height: 1.05;
        color: #f0e8d8;
        letter-spacing: -0.02em;
        margin: 0 0 0.6rem 0;
    }
    .hero-title span { color: #c8a96e; }
    .hero-subtitle {
        font-size: 1.05rem;
        color: #8a8070;
        font-style: italic;
        margin-bottom: 0;
    }
    .hero-line {
        width: 60px;
        height: 2px;
        background: linear-gradient(90deg, #c8a96e, transparent);
        margin: 1.6rem auto 0;
    }

    /* ── Input section ── */
    .input-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.7rem;
        letter-spacing: 0.22em;
        color: #c8a96e;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
        display: block;
    }
    div[data-testid="stTextInput"] input {
        background: #14161c !important;
        border: 1px solid #2e2a22 !important;
        border-radius: 4px !important;
        color: #f0e8d8 !important;
        font-family: 'Lora', serif !important;
        font-size: 1.05rem !important;
        padding: 0.75rem 1rem !important;
        transition: border-color 0.2s;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #c8a96e !important;
        box-shadow: 0 0 0 2px rgba(200,169,110,0.15) !important;
    }
    div[data-testid="stTextInput"] input::placeholder { color: #4a4540 !important; }

    /* ── Primary button ── */
    div[data-testid="stButton"] > button[kind="primary"],
    div[data-testid="stButton"] > button {
        background: #c8a96e !important;
        color: #0b0c10 !important;
        border: none !important;
        border-radius: 4px !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        letter-spacing: 0.06em !important;
        padding: 0.65rem 2rem !important;
        transition: background 0.2s, transform 0.1s !important;
    }
    div[data-testid="stButton"] > button:hover {
        background: #dbbe84 !important;
        transform: translateY(-1px) !important;
    }

    /* ── Agent step cards ── */
    .step-card {
        background: #13151b;
        border: 1px solid #1e2028;
        border-radius: 6px;
        padding: 1.4rem 1.6rem;
        margin: 1rem 0;
        position: relative;
        overflow: hidden;
        transition: border-color 0.3s;
    }
    .step-card.active  { border-color: #c8a96e; }
    .step-card.done    { border-color: #3a5a3a; }
    .step-card.waiting { opacity: 0.45; }

    .step-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 3px; height: 100%;
        background: #2e2a22;
        border-radius: 6px 0 0 6px;
    }
    .step-card.active::before  { background: #c8a96e; }
    .step-card.done::before    { background: #4a8a4a; }

    .step-header {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        margin-bottom: 0.5rem;
    }
    .step-badge {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.65rem;
        letter-spacing: 0.18em;
        padding: 0.2rem 0.55rem;
        border-radius: 3px;
        text-transform: uppercase;
        background: #1e2028;
        color: #6a6458;
    }
    .step-badge.active  { background: rgba(200,169,110,0.18); color: #c8a96e; }
    .step-badge.done    { background: rgba(74,138,74,0.18);   color: #6aba6a; }

    .step-title {
        font-family: 'Syne', sans-serif;
        font-weight: 700;
        font-size: 1rem;
        color: #d8d0c0;
        margin: 0;
    }
    .step-icon { font-size: 1.1rem; }

    .step-desc {
        font-size: 0.85rem;
        color: #6a6458;
        font-style: italic;
        margin: 0;
    }

    /* ── Result text boxes ── */
    .result-box {
        background: #0d0f14;
        border: 1px solid #1e2028;
        border-radius: 4px;
        padding: 1rem 1.2rem;
        margin-top: 0.9rem;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.78rem;
        line-height: 1.7;
        color: #a09888;
        max-height: 260px;
        overflow-y: auto;
        white-space: pre-wrap;
        word-break: break-word;
    }
    .result-box::-webkit-scrollbar { width: 4px; }
    .result-box::-webkit-scrollbar-track { background: transparent; }
    .result-box::-webkit-scrollbar-thumb { background: #2e2a22; border-radius: 2px; }

    /* ── Final report ── */
    .report-wrapper {
        background: #0f1018;
        border: 1px solid #c8a96e40;
        border-radius: 6px;
        padding: 2rem 2.4rem;
        margin-top: 1.2rem;
        position: relative;
    }
    .report-wrapper::before {
        content: 'FINAL REPORT';
        position: absolute;
        top: -0.6rem; left: 1.4rem;
        background: #0b0c10;
        padding: 0 0.5rem;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.62rem;
        letter-spacing: 0.28em;
        color: #c8a96e;
    }
    .report-text {
        font-size: 0.97rem;
        line-height: 1.85;
        color: #d8cfc0;
        white-space: pre-wrap;
    }

    /* ── Critic feedback ── */
    .feedback-wrapper {
        background: #0f1018;
        border: 1px solid #4a8a4a40;
        border-radius: 6px;
        padding: 1.6rem 2rem;
        margin-top: 1.2rem;
        position: relative;
    }
    .feedback-wrapper::before {
        content: 'CRITIC FEEDBACK';
        position: absolute;
        top: -0.6rem; left: 1.4rem;
        background: #0b0c10;
        padding: 0 0.5rem;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.62rem;
        letter-spacing: 0.28em;
        color: #6aba6a;
    }
    .feedback-text {
        font-size: 0.92rem;
        line-height: 1.8;
        color: #c0c8b0;
        white-space: pre-wrap;
    }

    /* ── Divider ── */
    .section-divider {
        border: none;
        border-top: 1px solid #1a1c22;
        margin: 2.5rem 0;
    }

    /* ── Section heading ── */
    .section-heading {
        font-family: 'Syne', sans-serif;
        font-size: 0.72rem;
        letter-spacing: 0.3em;
        text-transform: uppercase;
        color: #4a4540;
        margin-bottom: 1.2rem;
    }

    /* ── Spinner override ── */
    .stSpinner > div { border-top-color: #c8a96e !important; }

    /* ── Success/error messages ── */
    div[data-testid="stAlert"] {
        border-radius: 4px !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.82rem !important;
    }

    /* ── Columns gap ── */
    div[data-testid="column"] { padding: 0 0.6rem; }

    /* ── Scrollbar global ── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #0b0c10; }
    ::-webkit-scrollbar-thumb { background: #2e2a22; border-radius: 3px; }

    /* ── Pulse animation for active step ── */
    @keyframes pulse-border {
        0%   { box-shadow: 0 0 0 0   rgba(200,169,110,0.25); }
        70%  { box-shadow: 0 0 0 8px rgba(200,169,110,0);    }
        100% { box-shadow: 0 0 0 0   rgba(200,169,110,0);    }
    }
    .step-card.active { animation: pulse-border 2s infinite; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
#  Session state defaults
# ─────────────────────────────────────────────
for key in ("ran", "state", "step"):
    if key not in st.session_state:
        st.session_state[key] = False if key == "ran" else ({} if key == "state" else 0)

# ─────────────────────────────────────────────
#  Hero
# ─────────────────────────────────────────────
st.markdown(
    """
    <div class="hero">
        <p class="hero-eyebrow">Multi-Agent Intelligence System</p>
        <h1 class="hero-title">Research <span>Pipeline</span></h1>
        <p class="hero-subtitle">Search · Read · Write · Critique</p>
        <div class="hero-line"></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
#  Input row
# ─────────────────────────────────────────────
col_input, col_btn = st.columns([5, 1], gap="small")

with col_input:
    st.markdown('<span class="input-label">Research Topic</span>', unsafe_allow_html=True)
    topic = st.text_input(
        label="topic",
        placeholder="e.g.  Quantum computing in drug discovery",
        label_visibility="collapsed",
        key="topic_input",
    )

with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)   # align vertically
    run_btn = st.button("▶  Run", use_container_width=True)

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  Helper: render a step card
# ─────────────────────────────────────────────
# ─────────────────────────────────────────────
#  step_card_html — must be defined before run_pipeline
# ─────────────────────────────────────────────
def step_card_html(icon, title, desc, status, result_text=None):
    """Return an HTML string for one agent step card.
    status: 'waiting' | 'active' | 'done'
    """
    badge_map = {"waiting": "", "active": "Running…", "done": "Complete"}
    html = f"""
    <div class="step-card {status}">
        <div class="step-header">
            <span class="step-icon">{icon}</span>
            <p class="step-title">{title}</p>
            <span class="step-badge {status}">{badge_map[status]}</span>
        </div>
        <p class="step-desc">{desc}</p>"""
    if result_text and status == "done":
        safe = (
            str(result_text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        html += f'<div class="result-box">{safe}</div>'
    html += "</div>"
    return html


# ─────────────────────────────────────────────
#  Pipeline runner
# ─────────────────────────────────────────────
def run_pipeline(topic: str):
    state = {}

    placeholders = {
        "search":  st.empty(),
        "reader":  st.empty(),
        "writer":  st.empty(),
        "critic":  st.empty(),
    }

    # --- initial render: all waiting
    placeholders["search"].markdown(step_card_html("🔍", "Search Agent",
        "Discovers recent, reliable information across the web.", "waiting"), unsafe_allow_html=True)
    placeholders["reader"].markdown(step_card_html("📄", "Reader Agent",
        "Selects the best URL and scrapes deep content.", "waiting"), unsafe_allow_html=True)
    placeholders["writer"].markdown(step_card_html("✍️", "Writer Agent",
        "Synthesises findings into a structured report.", "waiting"), unsafe_allow_html=True)
    placeholders["critic"].markdown(step_card_html("🧐", "Critic Agent",
        "Evaluates the report for accuracy and completeness.", "waiting"), unsafe_allow_html=True)

    # ── STEP 1: SEARCH ──
    placeholders["search"].markdown(step_card_html("🔍", "Search Agent",
        "Searching for recent and reliable information…", "active"), unsafe_allow_html=True)

    with st.spinner("Search agent scanning the web…"):
        search_agent = build_search_agents()
        search_result = search_agent.invoke({
            "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
        })
    state["search_results"] = search_result["messages"][-1].content

    placeholders["search"].markdown(
        step_card_html("🔍", "Search Agent", "Web search complete.", "done",
                       state["search_results"]),
        unsafe_allow_html=True,
    )

    # ── STEP 2: READER ──
    placeholders["reader"].markdown(step_card_html("📄", "Reader Agent",
        "Picking the best URL and scraping content…", "active"), unsafe_allow_html=True)

    with st.spinner("Reader agent scraping selected source…"):
        reader_agent = build_reader_agent()
        reader_result = reader_agent.invoke({
            "messages": [("user",
                f"Based on the following search results about '{topic}', "
                f"pick the most relevant URL and scrape it for deeper content.\n\n"
                f"Search Results:\n{state['search_results'][:800]}")]
        })
    state["scraped_content"] = reader_result["messages"][-1].content

    placeholders["reader"].markdown(
        step_card_html("📄", "Reader Agent", "Scraping complete.", "done",
                       state["scraped_content"]),
        unsafe_allow_html=True,
    )

    # ── STEP 3: WRITER ──
    placeholders["writer"].markdown(step_card_html("✍️", "Writer Agent",
        "Drafting the research report…", "active"), unsafe_allow_html=True)

    with st.spinner("Writer agent composing the report…"):
        research_combined = (
            f"SEARCH RESULTS:\n{state['search_results']}\n\n"
            f"SCRAPED CONTENT:\n{state['scraped_content']}"
        )
        state["report"] = str(writer_chain.invoke({
            "topic": topic,
            "research": research_combined,
        }))

    placeholders["writer"].markdown(
        step_card_html("✍️", "Writer Agent", "Draft complete.", "done",
                       state["report"][:400] + "…"),
        unsafe_allow_html=True,
    )

    # ── STEP 4: CRITIC ──
    placeholders["critic"].markdown(step_card_html("🧐", "Critic Agent",
        "Reviewing the report for quality…", "active"), unsafe_allow_html=True)

    with st.spinner("Critic agent reviewing the draft…"):
        state["feedback"] = str(critic_chain.invoke({"report": state["report"]}))

    placeholders["critic"].markdown(
        step_card_html("🧐", "Critic Agent", "Review complete.", "done",
                       state["feedback"][:300] + "…"),
        unsafe_allow_html=True,
    )

    return state


# ─────────────────────────────────────────────
#  Trigger
# ─────────────────────────────────────────────
if run_btn:
    if not topic.strip():
        st.warning("Please enter a research topic before running the pipeline.")
    else:
        st.markdown('<p class="section-heading">Agent Pipeline</p>', unsafe_allow_html=True)
        result = run_pipeline(topic.strip())
        st.session_state["ran"]   = True
        st.session_state["state"] = result

# ─────────────────────────────────────────────
#  Results panel (shown after run)
# ─────────────────────────────────────────────
if st.session_state["ran"] and st.session_state["state"]:
    s = st.session_state["state"]
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    col_report, col_feedback = st.columns([3, 2], gap="medium")

    with col_report:
        st.markdown('<p class="section-heading">Full Report</p>', unsafe_allow_html=True)
        safe_report = (
            s.get("report", "")
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        st.markdown(
            f'<div class="report-wrapper"><div class="report-text">{safe_report}</div></div>',
            unsafe_allow_html=True,
        )
        st.download_button(
            label="⬇  Download Report",
            data=s.get("report", ""),
            file_name=f"report_{topic[:40].replace(' ','_')}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    with col_feedback:
        st.markdown('<p class="section-heading">Critic Review</p>', unsafe_allow_html=True)
        safe_feedback = (
            s.get("feedback", "")
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        st.markdown(
            f'<div class="feedback-wrapper"><div class="feedback-text">{safe_feedback}</div></div>',
            unsafe_allow_html=True,
        )
        st.download_button(
            label="⬇  Download Feedback",
            data=s.get("feedback", ""),
            file_name=f"feedback_{topic[:40].replace(' ','_')}.txt",
            mime="text/plain",
            use_container_width=True,
        )

# ─────────────────────────────────────────────
#  Footer
# ─────────────────────────────────────────────
st.markdown(
    """
    <hr class='section-divider'>
    <p style="text-align:center; font-family:'IBM Plex Mono',monospace;
              font-size:0.65rem; letter-spacing:0.2em; color:#2e2a22;
              text-transform:uppercase;">
        Multi-Agent Research System &nbsp;·&nbsp; Powered by LangChain &amp; Claude
    </p>
    """,
    unsafe_allow_html=True,
)