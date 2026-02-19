"""AuditWatch SAR Narrative Generator -- Streamlit Application.

Features:
- JWT login with role-based access
- Loading animations during pipeline execution
- Live pattern detection visualization
- Confidence score breakdown chart
- Regulatory compliance checker
- Multi-format export (PDF, JSON, CSV, TXT)
- Real-time stats sidebar
- Multi-agent pipeline toggle
"""

import json
import sys
import time
import logging
from pathlib import Path
from datetime import datetime

import streamlit as st

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.config import CONFIG
from src.main import SARGenerator
from src.utils.auth import AuthManager
from src.utils.pdf_generator import generate_pdf

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# Page config (must be first Streamlit call)
# ------------------------------------------------------------------
st.set_page_config(
    page_title="AuditWatch - SAR Narrative Generator",
    page_icon="S",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------
# CSS Styles
# ------------------------------------------------------------------
st.markdown("""
<style>
    /* Root variables */
    :root {
        --primary: #1a237e;
        --primary-light: #3949ab;
        --accent: #0288d1;
        --success: #2e7d32;
        --warning: #ef6c00;
        --danger: #c62828;
        --bg-dark: #0a0a1a;
        --bg-card: #131328;
        --text-primary: #e0e0e0;
        --text-secondary: #9e9e9e;
        --border: #2a2a4a;
    }

    /* Hide Streamlit defaults */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Main background */
    .stApp {
        background: linear-gradient(135deg, var(--bg-dark) 0%, #0d1117 100%);
    }

    /* Card styling */
    .metric-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 20px;
        margin: 8px 0;
        transition: transform 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: var(--accent);
    }
    .metric-card h4 {
        color: var(--text-secondary);
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }
    .metric-card .metric-value {
        color: var(--text-primary);
        font-size: 1.8rem;
        font-weight: 700;
    }

    /* Status badges */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge-success { background: rgba(46,125,50,0.2); color: #66bb6a; border: 1px solid #2e7d32; }
    .badge-warning { background: rgba(239,108,0,0.2); color: #ffa726; border: 1px solid #ef6c00; }
    .badge-danger { background: rgba(198,40,40,0.2); color: #ef5350; border: 1px solid #c62828; }
    .badge-info { background: rgba(2,136,209,0.2); color: #29b6f6; border: 1px solid #0288d1; }

    /* Pipeline step visualization */
    .pipeline-step {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 12px 16px;
        margin: 6px 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .pipeline-step.active {
        border-color: var(--accent);
        background: rgba(2,136,209,0.08);
    }
    .pipeline-step.completed {
        border-color: var(--success);
        background: rgba(46,125,50,0.08);
    }
    .step-number {
        background: var(--primary);
        color: white;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.85rem;
        flex-shrink: 0;
    }
    .step-number.completed {
        background: var(--success);
    }
    .step-number.active {
        background: var(--accent);
        animation: pulse 1.5s infinite;
    }

    /* Pulse animation */
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(2,136,209,0.4); }
        70% { box-shadow: 0 0 0 10px rgba(2,136,209,0); }
        100% { box-shadow: 0 0 0 0 rgba(2,136,209,0); }
    }

    /* Score bar */
    .score-bar {
        background: #1e1e3e;
        border-radius: 8px;
        height: 24px;
        overflow: hidden;
        margin: 4px 0;
    }
    .score-fill {
        height: 100%;
        border-radius: 8px;
        transition: width 0.8s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        font-weight: 600;
        color: white;
    }
    .score-fill.low { background: linear-gradient(90deg, #2e7d32, #43a047); }
    .score-fill.medium { background: linear-gradient(90deg, #ef6c00, #fb8c00); }
    .score-fill.high { background: linear-gradient(90deg, #c62828, #e53935); }

    /* Compliance checklist */
    .compliance-item {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px 12px;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    .compliance-pass { color: #66bb6a; }
    .compliance-fail { color: #ef5350; }

    /* Login form */
    .login-container {
        max-width: 400px;
        margin: 100px auto;
        padding: 40px;
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 16px;
    }
    .login-title {
        text-align: center;
        color: var(--text-primary);
        font-size: 1.5rem;
        margin-bottom: 8px;
    }
    .login-subtitle {
        text-align: center;
        color: var(--text-secondary);
        font-size: 0.9rem;
        margin-bottom: 24px;
    }

    /* Header banner */
    .header-banner {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 50%, var(--accent) 100%);
        color: white;
        padding: 20px 30px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    .header-banner h1 {
        font-size: 1.6rem;
        margin: 0;
    }
    .header-banner p {
        font-size: 0.9rem;
        opacity: 0.85;
        margin: 4px 0 0 0;
    }

    /* Pattern detection list */
    .pattern-item {
        background: rgba(198,40,40,0.1);
        border-left: 3px solid var(--danger);
        padding: 8px 14px;
        margin: 4px 0;
        border-radius: 0 6px 6px 0;
        font-size: 0.9rem;
        color: var(--text-primary);
        animation: fadeInLeft 0.3s ease;
    }

    @keyframes fadeInLeft {
        from { opacity: 0; transform: translateX(-10px); }
        to { opacity: 1; transform: translateX(0); }
    }

    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: var(--bg-card);
    }

    /* Table styling */
    .comparison-table {
        width: 100%;
        border-collapse: collapse;
        margin: 12px 0;
    }
    .comparison-table th {
        background: var(--primary);
        color: white;
        padding: 10px 14px;
        text-align: left;
        font-size: 0.85rem;
    }
    .comparison-table td {
        padding: 8px 14px;
        border-bottom: 1px solid var(--border);
        color: var(--text-primary);
        font-size: 0.85rem;
    }
    .comparison-table tr:hover td {
        background: rgba(255,255,255,0.03);
    }
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------
# Session state init
# ------------------------------------------------------------------
def init_session():
    defaults = {
        "authenticated": False,
        "user_token": None,
        "user_info": None,
        "auth_manager": AuthManager(),
        "narrative": None,
        "explainability": None,
        "generation_log": [],
        "cases_processed": 0,
        "total_patterns": 0,
        "pipeline_mode": "direct",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


init_session()


# ------------------------------------------------------------------
# Auth functions
# ------------------------------------------------------------------
def login_page():
    """Render the login page."""
    st.markdown("""
    <div style="text-align:center; margin-top:60px;">
        <h1 style="color:#e0e0e0; font-size:2.2rem;">AuditWatch</h1>
        <p style="color:#9e9e9e; font-size:1rem; margin-bottom:40px;">
            SAR Narrative Generator -- Secure Access
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.form("login_form"):
            st.markdown("#### Sign In")
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            submitted = st.form_submit_button("Sign In", use_container_width=True)

            if submitted:
                if not username or not password:
                    st.error("Please enter both username and password.")
                    return

                auth = st.session_state.auth_manager
                token = auth.authenticate(username, password)
                if token:
                    st.session_state.authenticated = True
                    st.session_state.user_token = token
                    st.session_state.user_info = auth.get_user_info(token)
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please try again.")

        st.markdown("---")
        st.markdown("""
        <div style="text-align:center; color:#9e9e9e; font-size:0.8rem;">
            <p>Default accounts for demo:</p>
            <p><strong>admin</strong> / auditwatch2026</p>
            <p><strong>analyst_01</strong> / analyst123</p>
            <p><strong>reviewer_01</strong> / reviewer123</p>
        </div>
        """, unsafe_allow_html=True)


def logout():
    st.session_state.authenticated = False
    st.session_state.user_token = None
    st.session_state.user_info = None
    st.rerun()


# ------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------
def get_sample_cases():
    """Load sample case files."""
    cases_dir = project_root / "data" / "sample_cases"
    cases = {}
    if cases_dir.exists():
        for f in sorted(cases_dir.glob("*.json")):
            with open(f, "r", encoding="utf-8") as fh:
                cases[f.stem] = json.load(fh)
    return cases


def render_metric_card(label, value, col):
    """Render a styled metric card."""
    col.markdown(f"""
    <div class="metric-card">
        <h4>{label}</h4>
        <div class="metric-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)


def render_risk_badge(score):
    """Return HTML badge for risk score."""
    if score >= 70:
        return f'<span class="badge badge-danger">HIGH RISK ({score}/100)</span>'
    elif score >= 40:
        return f'<span class="badge badge-warning">MEDIUM RISK ({score}/100)</span>'
    else:
        return f'<span class="badge badge-success">LOW RISK ({score}/100)</span>'


def render_score_bar(label, value, max_val=100):
    """Render a horizontal score bar."""
    pct = min(100, int((value / max_val) * 100)) if max_val > 0 else 0
    css_class = "high" if pct >= 70 else "medium" if pct >= 40 else "low"
    return f"""
    <div style="margin: 6px 0;">
        <div style="display:flex; justify-content:space-between; font-size:0.8rem; color:#9e9e9e;">
            <span>{label}</span><span>{value}/{max_val}</span>
        </div>
        <div class="score-bar">
            <div class="score-fill {css_class}" style="width:{pct}%">{pct}%</div>
        </div>
    </div>
    """


def render_compliance_check(label, passed):
    """Render a regulatory compliance checklist item."""
    icon = "[PASS]" if passed else "[FAIL]"
    css_class = "compliance-pass" if passed else "compliance-fail"
    return f"""
    <div class="compliance-item">
        <span class="{css_class}" style="font-weight:700;">{icon}</span>
        <span style="color:#e0e0e0;">{label}</span>
    </div>
    """


# ------------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------------
def render_sidebar():
    """Render the sidebar with user info and stats."""
    user = st.session_state.user_info
    with st.sidebar:
        st.markdown(f"""
        <div style="padding:16px; background:#131328; border-radius:12px; margin-bottom:16px;">
            <div style="color:#e0e0e0; font-weight:600;">{user.get('name', 'User')}</div>
            <div style="color:#9e9e9e; font-size:0.8rem;">{user.get('role', 'analyst').upper()}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("**Session Stats**")
        st.metric("Cases Processed", st.session_state.cases_processed)
        st.metric("Patterns Detected", st.session_state.total_patterns)

        st.markdown("---")
        st.markdown("**Pipeline Mode**")
        mode = st.radio(
            "Select pipeline",
            ["Direct Pipeline", "Multi-Agent (A2A)"],
            index=0 if st.session_state.pipeline_mode == "direct" else 1,
            label_visibility="collapsed",
        )
        st.session_state.pipeline_mode = "direct" if mode == "Direct Pipeline" else "agents"

        if st.session_state.pipeline_mode == "agents":
            st.markdown("""
            <div style="background:rgba(2,136,209,0.1); border:1px solid #0288d1;
                        border-radius:8px; padding:10px; font-size:0.8rem; color:#29b6f6;">
                Multi-Agent mode uses 5 coordinated A2A agents:
                Coordinator, DataEnrichment, Typology, Narrative, Audit
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        if st.button("Sign Out", use_container_width=True):
            logout()


# ------------------------------------------------------------------
# Page 1: Input Case
# ------------------------------------------------------------------
def page_input():
    """Case input and generation page."""
    st.markdown("""
    <div class="header-banner">
        <h1>SAR Narrative Generator</h1>
        <p>AI-powered Suspicious Activity Report generation with full audit trail</p>
    </div>
    """, unsafe_allow_html=True)

    sample_cases = get_sample_cases()

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### Input Method")
        input_method = st.radio(
            "Choose input method",
            ["Load Sample Case", "Paste JSON"],
            label_visibility="collapsed",
        )

    with col2:
        if input_method == "Load Sample Case" and sample_cases:
            selected = st.selectbox(
                "Select a sample case",
                list(sample_cases.keys()),
            )
            case_json = sample_cases[selected]
            st.markdown(f"""
            <div class="metric-card">
                <h4>Selected Case</h4>
                <div style="color:#e0e0e0;">
                    <strong>Case ID:</strong> {case_json.get('case_id', 'N/A')}<br>
                    <strong>Alert:</strong> {case_json.get('alert_reason', 'N/A')}<br>
                    <strong>Transactions:</strong> {len(case_json.get('transactions', []))}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            case_json = None

    if input_method == "Paste JSON":
        json_text = st.text_area(
            "Paste case JSON",
            height=300,
            placeholder='{"case_id": "...", "customer": {...}, "transactions": [...], "alert_reason": "..."}',
        )
        if json_text:
            try:
                case_json = json.loads(json_text)
            except json.JSONDecodeError as e:
                st.error("Invalid JSON: %s" % str(e))
                case_json = None

    st.markdown("---")

    # Generate button
    if st.button("Generate SAR Narrative", use_container_width=True, type="primary"):
        if not case_json:
            st.error("Please provide case data before generating.")
            return

        _run_generation(case_json)


def _run_generation(case_json):
    """Run the SAR generation pipeline with live visualization."""
    pipeline_steps = [
        "Parsing and validating case input",
        "Calculating transaction statistics",
        "Detecting suspicious patterns",
        "Retrieving templates and classifying typology",
        "Generating SAR narrative via LLM",
        "Building explainability report",
    ]

    # Pipeline visualization container
    step_container = st.container()
    with step_container:
        st.markdown("#### Pipeline Execution")
        step_placeholders = []
        for i, step_name in enumerate(pipeline_steps):
            ph = st.empty()
            ph.markdown(f"""
            <div class="pipeline-step">
                <div class="step-number">{i + 1}</div>
                <span style="color:#9e9e9e;">{step_name}</span>
            </div>
            """, unsafe_allow_html=True)
            step_placeholders.append(ph)

    # Pattern detection container
    pattern_container = st.empty()
    result_container = st.container()
    completed_steps = []

    def progress_callback(step, message):
        """Update pipeline visualization in real-time."""
        for j in range(len(pipeline_steps)):
            if j + 1 < step:
                step_placeholders[j].markdown(f"""
                <div class="pipeline-step completed">
                    <div class="step-number completed">{j + 1}</div>
                    <span style="color:#66bb6a;">{pipeline_steps[j]} -- Done</span>
                </div>
                """, unsafe_allow_html=True)
            elif j + 1 == step:
                step_placeholders[j].markdown(f"""
                <div class="pipeline-step active">
                    <div class="step-number active">{j + 1}</div>
                    <span style="color:#29b6f6;">{message}</span>
                </div>
                """, unsafe_allow_html=True)
        completed_steps.append(step)

    try:
        generator = SARGenerator()

        if st.session_state.pipeline_mode == "agents":
            # Multi-agent pipeline
            with st.status("Running Multi-Agent Pipeline...", expanded=True) as status:
                st.write("Initializing CoordinatorAgent...")
                result = generator.generate_with_agents(
                    case_json,
                    user_id=st.session_state.user_info.get("user_id", "system"),
                )
                status.update(label="Multi-Agent Pipeline Complete", state="complete")

                if result.get("status") == "completed":
                    narrative_data = result["results"]["narrative"]["narrative"]
                    from src.models.sar_output import SARNarrative, ExplainabilityOutput
                    narrative = SARNarrative(**narrative_data)

                    data_result = result["results"]["data"]
                    typology_result = result["results"]["typology"]

                    explainability = ExplainabilityOutput(
                        case_id=narrative.case_id,
                        why_suspicious=data_result.get("patterns", []),
                        typology_matched=typology_result.get("typology", ""),
                        typology_confidence=typology_result.get("confidence", 0),
                        templates_used=[],
                        model_reasoning="Multi-agent pipeline",
                        data_points_accessed=[],
                        rules_matched=data_result.get("patterns", []),
                        calculations={
                            "risk_score": str(data_result.get("risk_score", 0)),
                        },
                    )

                    st.session_state.narrative = narrative
                    st.session_state.explainability = explainability
                    st.session_state.cases_processed += 1
                    st.session_state.total_patterns += len(data_result.get("patterns", []))

                    # Show agent execution summary
                    st.markdown("#### Agent Execution Summary")
                    for agent_step in result.get("agent_steps", []):
                        agent_name = agent_step.get("agent", "unknown")
                        duration = agent_step.get("duration_seconds", 0)
                        status_val = agent_step.get("status", "unknown")
                        badge_class = "badge-success" if status_val == "completed" else "badge-danger"
                        st.markdown(f"""
                        <div class="pipeline-step completed">
                            <span style="color:#e0e0e0; flex:1;">{agent_name}</span>
                            <span class="badge {badge_class}">{status_val}</span>
                            <span style="color:#9e9e9e; font-size:0.8rem;">{duration:.3f}s</span>
                        </div>
                        """, unsafe_allow_html=True)

                    st.success("Narrative generated successfully. Switch to the Review tab.")
                else:
                    st.error("Multi-agent pipeline failed: %s" % result.get("error", "Unknown"))
                    return

        else:
            # Direct pipeline with progress callback
            narrative, explainability = generator.generate(
                case_json,
                user_id=st.session_state.user_info.get("user_id", "system"),
                progress_callback=progress_callback,
            )

            # Mark all steps complete
            for j in range(len(pipeline_steps)):
                step_placeholders[j].markdown(f"""
                <div class="pipeline-step completed">
                    <div class="step-number completed">{j + 1}</div>
                    <span style="color:#66bb6a;">{pipeline_steps[j]} -- Done</span>
                </div>
                """, unsafe_allow_html=True)

            st.session_state.narrative = narrative
            st.session_state.explainability = explainability
            st.session_state.cases_processed += 1
            st.session_state.total_patterns += len(narrative.red_flags)

            # Live pattern detection display
            if narrative.red_flags:
                with result_container:
                    st.markdown("#### Patterns Detected in Real-Time")
                    for pattern in narrative.red_flags:
                        st.markdown(
                            f'<div class="pattern-item">{pattern}</div>',
                            unsafe_allow_html=True,
                        )

            st.success("Narrative generated successfully. Switch to the Review tab.")

    except Exception as e:
        st.error("Pipeline error: %s" % str(e))
        logger.exception("Pipeline error")


# ------------------------------------------------------------------
# Page 2: Narrative Review
# ------------------------------------------------------------------
def page_narrative():
    """Review and edit the generated narrative."""
    st.markdown("""
    <div class="header-banner">
        <h1>Narrative Review</h1>
        <p>Review, edit, and approve the generated SAR narrative</p>
    </div>
    """, unsafe_allow_html=True)

    narrative = st.session_state.narrative
    explainability = st.session_state.explainability

    if not narrative:
        st.info("No narrative generated yet. Go to the Input page to generate one.")
        return

    # Risk overview
    col1, col2, col3, col4 = st.columns(4)
    render_metric_card("Case ID", narrative.case_id, col1)
    render_metric_card("Risk Score", "%d/100" % narrative.confidence_score, col2)
    render_metric_card("Typology", narrative.typology or "N/A", col3)
    render_metric_card("Patterns", str(len(narrative.red_flags)), col4)

    st.markdown("---")

    # Risk score badge
    st.markdown(render_risk_badge(narrative.confidence_score), unsafe_allow_html=True)

    # Confidence score breakdown
    st.markdown("#### Risk Score Breakdown")
    _render_confidence_breakdown(narrative, explainability)

    st.markdown("---")

    # Narrative text
    st.markdown("#### Generated Narrative")
    edited_text = st.text_area(
        "Edit the narrative if needed:",
        value=narrative.narrative_text,
        height=400,
        label_visibility="collapsed",
    )

    # Approval actions
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("Approve Narrative", use_container_width=True, type="primary"):
            try:
                generator = SARGenerator()
                edits = edited_text if edited_text != narrative.narrative_text else None
                generator.approve_narrative(
                    narrative.case_id,
                    st.session_state.user_info.get("user_id", "system"),
                    edited_text=edits,
                )
                st.success("Narrative approved and logged to audit trail.")
            except Exception as e:
                st.error("Approval error: %s" % str(e))

    with col_b:
        if st.button("Reject Narrative", use_container_width=True):
            reason = st.text_input("Rejection reason:", key="reject_reason")
            if reason:
                try:
                    generator = SARGenerator()
                    generator.reject_narrative(
                        narrative.case_id,
                        st.session_state.user_info.get("user_id", "system"),
                        reason=reason,
                    )
                    st.warning("Narrative rejected.")
                except Exception as e:
                    st.error("Rejection error: %s" % str(e))

    # Regulatory compliance checker
    st.markdown("---")
    st.markdown("#### Regulatory Compliance Checker")
    _render_compliance_checker(narrative, explainability)


def _render_confidence_breakdown(narrative, explainability):
    """Render the risk score breakdown as component bars."""
    patterns = narrative.red_flags if narrative.red_flags else []
    pattern_score = min(len(patterns) * 10, 40)

    # Parse risk score into components
    risk = narrative.confidence_score
    kyc_map = {"High": 15, "Medium": 5, "Low": 0}

    stats = narrative.transaction_stats or {}
    kyc_score = 5  # Default medium

    remaining = max(0, risk - pattern_score - kyc_score)
    volume_score = min(remaining, 25)
    counterparty_score = max(0, remaining - volume_score)

    components_html = ""
    components_html += render_score_bar("Pattern Detection", pattern_score, 40)
    components_html += render_score_bar("Volume Deviation", volume_score, 25)
    components_html += render_score_bar("KYC Risk Rating", kyc_score, 15)
    components_html += render_score_bar("Counterparty Risk", counterparty_score, 10)
    components_html += "<div style='margin-top:12px;'>"
    components_html += render_score_bar("TOTAL RISK SCORE", risk, 100)
    components_html += "</div>"

    st.markdown(components_html, unsafe_allow_html=True)


def _render_compliance_checker(narrative, explainability):
    """Render the regulatory compliance checklist."""
    text = narrative.narrative_text.lower() if narrative.narrative_text else ""

    checks = [
        ("PMLA Section 12 reference included",
         "pmla" in text and "section 12" in text),
        ("Customer identification details present",
         "account" in text and "customer" in text),
        ("Suspicious activity description provided",
         "suspicious" in text or "suspicion" in text),
        ("Transaction period specified",
         any(str(y) in text for y in range(2020, 2030))),
        ("Red flag indicators documented",
         len(narrative.red_flags) > 0),
        ("Typology classification included",
         bool(narrative.typology and narrative.typology != "unknown")),
        ("FIU-IND filing recommendation present",
         "fiu" in text or "filing" in text),
        ("RBI Master Direction compliance",
         "rbi" in text or "master direction" in text),
        ("Conclusion and recommendation section exists",
         "conclusion" in text or "recommendation" in text),
    ]

    passed = sum(1 for _, v in checks if v)
    total = len(checks)

    st.markdown(f"""
    <div style="margin-bottom:12px;">
        <span style="color:#e0e0e0; font-weight:600;">Compliance Score: {passed}/{total}</span>
        <span class="badge {'badge-success' if passed >= 7 else 'badge-warning' if passed >= 5 else 'badge-danger'}">
            {'COMPLIANT' if passed >= 7 else 'PARTIAL' if passed >= 5 else 'NON-COMPLIANT'}
        </span>
    </div>
    """, unsafe_allow_html=True)

    html = ""
    for label, passed_check in checks:
        html += render_compliance_check(label, passed_check)
    st.markdown(html, unsafe_allow_html=True)


# ------------------------------------------------------------------
# Page 3: Audit Trail
# ------------------------------------------------------------------
def page_audit():
    """Display the audit trail for the current case."""
    st.markdown("""
    <div class="header-banner">
        <h1>Audit Trail</h1>
        <p>Complete regulatory traceability for every decision point</p>
    </div>
    """, unsafe_allow_html=True)

    narrative = st.session_state.narrative
    if not narrative:
        st.info("No narrative generated yet. Generate a case first.")
        return

    try:
        generator = SARGenerator()
        trail = generator.get_audit_trail(narrative.case_id)

        if not trail:
            st.info("No audit events found for case %s." % narrative.case_id)
            return

        st.markdown(f"**{len(trail)} audit events** for case **{narrative.case_id}**")

        for i, event in enumerate(trail):
            event_type = event.get("event_type", "unknown")
            timestamp = event.get("timestamp", "")
            user_id = event.get("user_id", "system")

            with st.expander(
                "%d. %s  |  %s  |  %s" % (i + 1, event_type.upper(), timestamp, user_id)
            ):
                # Show metadata
                metadata = event.get("metadata")
                if metadata:
                    if isinstance(metadata, str):
                        try:
                            metadata = json.loads(metadata)
                        except (json.JSONDecodeError, TypeError):
                            pass
                    st.json(metadata)

                # Show other fields
                for field in ["input_data", "retrieved_context", "llm_reasoning"]:
                    value = event.get(field)
                    if value:
                        st.markdown(f"**{field.replace('_', ' ').title()}:**")
                        if isinstance(value, (dict, list)):
                            st.json(value)
                        else:
                            st.text(str(value)[:1000])

    except Exception as e:
        st.error("Error loading audit trail: %s" % str(e))


# ------------------------------------------------------------------
# Page 4: Export
# ------------------------------------------------------------------
def page_export():
    """Multi-format export page."""
    st.markdown("""
    <div class="header-banner">
        <h1>Export Reports</h1>
        <p>Export SAR narratives and audit trails in multiple formats</p>
    </div>
    """, unsafe_allow_html=True)

    narrative = st.session_state.narrative
    if not narrative:
        st.info("No narrative generated yet. Generate a case first.")
        return

    st.markdown("#### Export Narrative")

    col1, col2 = st.columns(2)

    with col1:
        # PDF export
        st.markdown("**PDF Report**")
        try:
            pdf_data = generate_pdf(narrative, narrative.case_id)
            st.download_button(
                "Download PDF",
                data=pdf_data,
                file_name="SAR_%s.pdf" % narrative.case_id,
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as e:
            st.error("PDF generation failed: %s" % str(e))

        # JSON export
        st.markdown("**JSON Export**")
        json_data = json.dumps(narrative.model_dump(), indent=2, default=str)
        st.download_button(
            "Download JSON",
            data=json_data,
            file_name="SAR_%s.json" % narrative.case_id,
            mime="application/json",
            use_container_width=True,
        )

    with col2:
        # TXT export
        st.markdown("**Plain Text**")
        txt_data = "SUSPICIOUS TRANSACTION REPORT\n"
        txt_data += "Case ID: %s\n" % narrative.case_id
        txt_data += "Generated: %s\n" % datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        txt_data += "=" * 60 + "\n\n"
        txt_data += narrative.narrative_text
        st.download_button(
            "Download TXT",
            data=txt_data,
            file_name="SAR_%s.txt" % narrative.case_id,
            mime="text/plain",
            use_container_width=True,
        )

        # CSV export (audit trail)
        st.markdown("**Audit Trail CSV**")
        try:
            generator = SARGenerator()
            csv_data = generator.export_audit(narrative.case_id, fmt="csv")
            st.download_button(
                "Download Audit CSV",
                data=csv_data,
                file_name="audit_%s.csv" % narrative.case_id,
                mime="text/csv",
                use_container_width=True,
            )
        except Exception as e:
            st.error("CSV export failed: %s" % str(e))

    # Audit JSON export
    st.markdown("---")
    st.markdown("#### Export Audit Trail")
    try:
        generator = SARGenerator()
        audit_json = generator.export_audit(narrative.case_id, fmt="json")
        st.download_button(
            "Download Audit Trail JSON",
            data=audit_json,
            file_name="audit_%s.json" % narrative.case_id,
            mime="application/json",
            use_container_width=True,
        )
    except Exception as e:
        st.error("Audit export failed: %s" % str(e))


# ------------------------------------------------------------------
# Page 5: Architecture
# ------------------------------------------------------------------
def page_architecture():
    """Show the MCP/A2A architecture."""
    st.markdown("""
    <div class="header-banner">
        <h1>System Architecture</h1>
        <p>MCP Tool Servers and A2A Multi-Agent Architecture</p>
    </div>
    """, unsafe_allow_html=True)

    # MCP Servers
    st.markdown("#### MCP Tool Servers")
    st.markdown("Real, callable MCP tool servers wrapping pipeline components:")

    try:
        from src.agents.mcp_servers import (
            TransactionAnalyzerServer,
            SARTemplateServer,
            AuditTrailServer,
        )

        servers = [
            ("Transaction Analyzer", TransactionAnalyzerServer),
            ("SAR Template Engine", SARTemplateServer),
            ("Audit Trail Manager", AuditTrailServer),
        ]

        for name, ServerClass in servers:
            server = ServerClass()
            tools = server.list_tools()
            with st.expander("%s -- %d tools" % (name, len(tools))):
                for tool in tools:
                    st.markdown(f"""
                    <div class="pipeline-step">
                        <div class="step-number">{tool['name'][:1].upper()}</div>
                        <div>
                            <strong style="color:#e0e0e0;">{tool['name']}</strong><br>
                            <span style="color:#9e9e9e; font-size:0.85rem;">{tool['description']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    except Exception as e:
        st.error("Error loading MCP servers: %s" % str(e))

    st.markdown("---")

    # A2A Agents
    st.markdown("#### A2A Multi-Agent Architecture")
    st.markdown("Specialized agents orchestrated by the CoordinatorAgent:")

    try:
        from src.agents.a2a_agents import (
            CoordinatorAgent,
            DataEnrichmentAgent,
            TypologyAgent,
            NarrativeAgent,
            AuditAgent,
        )

        agents = [
            CoordinatorAgent(),
            DataEnrichmentAgent(),
            TypologyAgent(),
            NarrativeAgent(),
            AuditAgent(),
        ]

        for agent in agents:
            card = agent.agent_card()
            skills = card.get("skills", [])
            with st.expander("%s -- %d skills" % (card["name"], len(skills))):
                st.markdown(
                    '<span class="badge badge-info">v%s</span>' % card.get("version", "1.0"),
                    unsafe_allow_html=True,
                )
                st.markdown("_%s_" % card["description"])
                for skill in skills:
                    st.markdown(
                        "- **%s**: %s" % (skill["name"], skill["description"])
                    )
    except Exception as e:
        st.error("Error loading A2A agents: %s" % str(e))


# ------------------------------------------------------------------
# Page 6: Settings (admin only)
# ------------------------------------------------------------------
def page_settings():
    """Settings page (admin only)."""
    st.markdown("""
    <div class="header-banner">
        <h1>Settings</h1>
        <p>System configuration and administration</p>
    </div>
    """, unsafe_allow_html=True)

    user = st.session_state.user_info
    if user.get("role") != "admin":
        st.warning("Settings are restricted to administrators.")
        return

    st.markdown("#### Current Configuration")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**LLM Settings**")
        st.text("Model: %s" % CONFIG["llm"]["model"])
        st.text("Temperature: %s" % CONFIG["llm"]["temperature"])
        st.text("Max Tokens: %s" % CONFIG["llm"]["max_tokens"])
        st.text("Base URL: %s" % CONFIG["llm"]["base_url"])

    with col2:
        st.markdown("**Database Settings**")
        st.text("Type: %s" % CONFIG["database"].get("type", "sqlite"))
        st.text("Path: %s" % CONFIG["database"].get("sqlite_path", "N/A"))

    st.markdown("---")
    st.markdown("**Security Settings**")
    st.text("PII Anonymization: %s" % CONFIG["security"].get("anonymize_pii", True))
    st.text("Max Input Length: %s" % CONFIG["security"].get("max_input_length", 100000))


# ------------------------------------------------------------------
# Main App Router
# ------------------------------------------------------------------
def main():
    """Main application entry point."""
    if not st.session_state.authenticated:
        login_page()
        return

    render_sidebar()

    # Navigation
    pages = {
        "Input Case": page_input,
        "Review Narrative": page_narrative,
        "Audit Trail": page_audit,
        "Export": page_export,
        "Architecture": page_architecture,
    }

    # Admin-only pages
    user = st.session_state.user_info
    if user and user.get("role") == "admin":
        pages["Settings"] = page_settings

    selected = st.sidebar.radio("Navigation", list(pages.keys()), label_visibility="collapsed")
    pages[selected]()


if __name__ == "__main__":
    main()
