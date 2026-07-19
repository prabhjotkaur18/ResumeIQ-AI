import streamlit as st
import time
import base64
from datetime import datetime

from backend.resume_reader import extract_pdf_text, extract_docx_text
from backend.gemini_service import analyze_resume

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="ResumeIQ AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================================
# SESSION STATE
# ==========================================================

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

if "ai_result" not in st.session_state:
    st.session_state.ai_result = None

if "resume_text" not in st.session_state:
    st.session_state.resume_text = None


def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"


# ==========================================================
# THEME TOKENS
# ==========================================================

if st.session_state.theme == "dark":
    THEME = {
        "bg_grad": "radial-gradient(circle at 15% 0%, #1b1140 0%, #0b0d1f 45%, #05060f 100%)",
        "surface": "rgba(255, 255, 255, 0.055)",
        "surface_border": "rgba(255, 255, 255, 0.10)",
        "surface_hover": "rgba(255, 255, 255, 0.09)",
        "text_primary": "#F5F6FA",
        "text_secondary": "#A6A9BE",
        "text_muted": "#71748C",
        "accent_a": "#7C5CFF",
        "accent_b": "#3AD6D6",
        "accent_c": "#FF6FD8",
        "shadow": "0 8px 32px rgba(0,0,0,0.45)",
        "header_bg": "rgba(10, 10, 20, 0.55)",
        "input_bg": "rgba(255,255,255,0.06)",
        "success": "#3ADCA6",
        "warn": "#FFB25B",
        "track": "rgba(255,255,255,0.09)",
    }
else:
    THEME = {
        "bg_grad": "radial-gradient(circle at 15% 0%, #EEF0FF 0%, #F7F8FC 45%, #FFFFFF 100%)",
        "surface": "rgba(255, 255, 255, 0.75)",
        "surface_border": "rgba(15, 23, 42, 0.08)",
        "surface_hover": "rgba(255, 255, 255, 0.95)",
        "text_primary": "#12131C",
        "text_secondary": "#4B4E63",
        "text_muted": "#8A8DA3",
        "accent_a": "#6D4CFF",
        "accent_b": "#0FB8B8",
        "accent_c": "#E6449C",
        "shadow": "0 8px 32px rgba(30, 30, 60, 0.10)",
        "header_bg": "rgba(255, 255, 255, 0.65)",
        "input_bg": "rgba(15,23,42,0.04)",
        "success": "#0EA472",
        "warn": "#B3690A",
        "track": "rgba(15,23,42,0.08)",
    }

T = THEME

# ==========================================================
# GLOBAL CSS
# ==========================================================

st.markdown(f"""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Space+Grotesk:wght@500;600;700&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', -apple-system, sans-serif;
}}

.stApp {{
    background: {T['bg_grad']};
    background-attachment: fixed;
    color: {T['text_primary']};
}}

#MainMenu, header, footer {{visibility: hidden;}}

.block-container {{
    padding-top: 5.5rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}}

* {{
    transition: background 0.25s ease, box-shadow 0.25s ease, transform 0.18s ease, border-color 0.25s ease, opacity 0.3s ease;
}}

/* ---------------- STICKY HEADER ---------------- */

.app-header {{
    position: fixed;
    top: 0; left: 0; right: 0;
    z-index: 999;
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    background: {T['header_bg']};
    border-bottom: 1px solid {T['surface_border']};
    padding: 14px 40px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}}

.brand {{
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 20px;
    display: flex;
    align-items: center;
    gap: 10px;
    color: {T['text_primary']};
    letter-spacing: -0.02em;
}}

.brand-badge {{
    background: linear-gradient(135deg, {T['accent_a']}, {T['accent_c']});
    width: 34px; height: 34px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 17px;
    box-shadow: 0 4px 14px rgba(124,92,255,0.4);
}}

.nav-pill {{
    font-size: 13px;
    color: {T['text_secondary']};
    background: {T['surface']};
    border: 1px solid {T['surface_border']};
    padding: 6px 14px;
    border-radius: 999px;
}}

/* ---------------- HERO ---------------- */

.hero-wrap {{
    text-align: center;
    padding: 30px 10px 10px 10px;
    animation: fadeInUp 0.8s ease both;
}}

.hero-eyebrow {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    font-weight: 600;
    color: {T['accent_a']};
    background: {T['surface']};
    border: 1px solid {T['surface_border']};
    padding: 6px 16px;
    border-radius: 999px;
    margin-bottom: 22px;
}}

.hero-title {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 56px;
    font-weight: 700;
    line-height: 1.08;
    letter-spacing: -0.03em;
    margin: 0 0 18px 0;
    background: linear-gradient(135deg, {T['text_primary']} 30%, {T['accent_a']} 75%, {T['accent_c']} 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}

.hero-sub {{
    font-size: 18px;
    color: {T['text_secondary']};
    max-width: 620px;
    margin: 0 auto 8px auto;
    line-height: 1.6;
}}

@keyframes fadeInUp {{
    from {{ opacity: 0; transform: translateY(18px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

@keyframes fadeIn {{
    from {{ opacity: 0; }}
    to {{ opacity: 1; }}
}}

@keyframes floaty {{
    0%, 100% {{ transform: translateY(0px); }}
    50% {{ transform: translateY(-10px); }}
}}

@keyframes pulseGlow {{
    0%, 100% {{ opacity: 0.55; }}
    50% {{ opacity: 1; }}
}}

@keyframes shimmer {{
    0% {{ background-position: -400px 0; }}
    100% {{ background-position: 400px 0; }}
}}

/* ---------------- GLASS CARD ---------------- */

.glass-card {{
    background: {T['surface']};
    border: 1px solid {T['surface_border']};
    border-radius: 20px;
    padding: 28px;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    box-shadow: {T['shadow']};
    animation: fadeInUp 0.6s ease both;
}}

.glass-card:hover {{
    border-color: {T['accent_a']}55;
    transform: translateY(-2px);
}}

.section-label {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 22px;
    font-weight: 600;
    letter-spacing: -0.01em;
    margin-bottom: 4px;
    color: {T['text_primary']};
    display: flex;
    align-items: center;
    gap: 10px;
}}

.section-caption {{
    color: {T['text_muted']};
    font-size: 14px;
    margin-bottom: 18px;
}}

/* ---------------- UPLOAD ZONE ---------------- */

[data-testid="stFileUploader"] {{
    background: {T['input_bg']};
    border: 1.5px dashed {T['surface_border']};
    border-radius: 16px;
    padding: 14px;
}}

[data-testid="stFileUploader"]:hover {{
    border-color: {T['accent_a']};
}}

[data-testid="stFileUploaderDropzone"] {{
    background: transparent;
}}

.stSelectbox > div > div {{
    background: {T['input_bg']};
    border-radius: 12px;
    border: 1px solid {T['surface_border']};
}}

label {{
    color: {T['text_secondary']} !important;
    font-weight: 600 !important;
    font-size: 13.5px !important;
}}

/* ---------------- BUTTONS ---------------- */

.stButton>button {{
    width: 100%;
    height: 54px;
    border-radius: 14px;
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 0.01em;
    background: linear-gradient(135deg, {T['accent_a']}, {T['accent_c']});
    background-size: 200% 200%;
    color: white;
    border: none;
    box-shadow: 0 8px 24px rgba(124,92,255,0.35);
    position: relative;
    overflow: hidden;
}}

.stButton>button:hover {{
    background-position: 100% 50%;
    box-shadow: 0 10px 30px rgba(124,92,255,0.5);
    transform: translateY(-2px);
}}

.stButton>button:active {{
    transform: translateY(0px);
}}

.stDownloadButton>button {{
    width: 100%;
    height: 48px;
    border-radius: 12px;
    font-weight: 700;
    background: {T['surface']};
    color: {T['text_primary']};
    border: 1px solid {T['surface_border']};
}}

.stDownloadButton>button:hover {{
    border-color: {T['accent_b']};
    color: {T['accent_b']};
}}

/* ---------------- FLOATING ILLUSTRATION (pre-upload) ---------------- */

.float-orb-wrap {{
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 34px 0 10px 0;
}}

.float-orb {{
    width: 130px;
    height: 130px;
    border-radius: 50%;
    background: conic-gradient(from 180deg, {T['accent_a']}, {T['accent_b']}, {T['accent_c']}, {T['accent_a']});
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 52px;
    animation: floaty 3.2s ease-in-out infinite;
    box-shadow: 0 20px 60px rgba(124,92,255,0.35);
    position: relative;
}}

.float-orb::after {{
    content: "";
    position: absolute;
    inset: -14px;
    border-radius: 50%;
    border: 1.5px dashed {T['accent_a']}66;
    animation: floaty 3.2s ease-in-out infinite reverse;
}}

.float-caption {{
    text-align: center;
    color: {T['text_muted']};
    font-size: 14px;
    margin-top: 18px;
}}

/* ---------------- BADGES ---------------- */

.badge-row {{
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}}

.badge {{
    padding: 8px 16px;
    border-radius: 999px;
    font-size: 13.5px;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    border: 1px solid transparent;
    animation: fadeInUp 0.5s ease both;
}}

.badge-found {{
    background: {T['success']}1A;
    color: {T['success']};
    border-color: {T['success']}40;
}}

.badge-missing {{
    background: {T['warn']}1A;
    color: {T['warn']};
    border-color: {T['warn']}40;
}}

/* ---------------- GAUGE ---------------- */

.gauge-wrap {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 10px;
}}

.gauge-label {{
    font-size: 13px;
    font-weight: 700;
    color: {T['text_muted']};
    text-transform: uppercase;
    letter-spacing: 0.06em;
}}

.gauge-value {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 15px;
    font-weight: 700;
    fill: {T['text_primary']};
}}

/* ---------------- METRIC STAT CARD ---------------- */

.stat-card {{
    background: {T['surface']};
    border: 1px solid {T['surface_border']};
    border-radius: 18px;
    padding: 22px;
    text-align: center;
    backdrop-filter: blur(16px);
}}

.stat-num {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 34px;
    font-weight: 700;
    background: linear-gradient(135deg, {T['accent_a']}, {T['accent_b']});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}

.stat-title {{
    color: {T['text_muted']};
    font-size: 13px;
    font-weight: 600;
    margin-top: 4px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}}

/* ---------------- PROGRESS BAR ---------------- */

.pbar-outer {{
    width: 100%;
    height: 12px;
    border-radius: 999px;
    background: {T['track']};
    overflow: hidden;
    margin-top: 8px;
}}

.pbar-inner {{
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, {T['accent_a']}, {T['accent_b']});
    background-size: 200% 100%;
    animation: shimmer 2.2s linear infinite;
}}

/* ---------------- TIMELINE ---------------- */

.timeline {{
    position: relative;
    padding-left: 34px;
    margin-top: 10px;
}}

.timeline::before {{
    content: "";
    position: absolute;
    left: 11px;
    top: 6px;
    bottom: 6px;
    width: 2px;
    background: linear-gradient(180deg, {T['accent_a']}, {T['accent_b']}55);
}}

.tl-item {{
    position: relative;
    margin-bottom: 22px;
    animation: fadeInUp 0.5s ease both;
}}

.tl-dot {{
    position: absolute;
    left: -34px;
    top: 2px;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: linear-gradient(135deg, {T['accent_a']}, {T['accent_c']});
    color: white;
    font-size: 12px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 12px rgba(124,92,255,0.4);
}}

.tl-content {{
    background: {T['surface']};
    border: 1px solid {T['surface_border']};
    border-radius: 14px;
    padding: 14px 18px;
    color: {T['text_secondary']};
    font-size: 14.5px;
}}

/* ---------------- SKILLS / CAREER / SUGGESTION BLOCKS ---------------- */

.info-block {{
    background: {T['surface']};
    border: 1px solid {T['surface_border']};
    border-left: 3px solid {T['accent_a']};
    border-radius: 12px;
    padding: 16px 18px;
    color: {T['text_secondary']};
    font-size: 14.5px;
    line-height: 1.55;
    margin-bottom: 10px;
}}

.suggestion-block {{
    background: {T['surface']};
    border: 1px solid {T['surface_border']};
    border-left: 3px solid {T['success']};
    border-radius: 12px;
    padding: 14px 18px;
    color: {T['text_secondary']};
    font-size: 14.5px;
    margin-bottom: 10px;
}}

/* ---------------- EXPANDER ---------------- */

.streamlit-expanderHeader, [data-testid="stExpander"] {{
    background: {T['surface']} !important;
    border: 1px solid {T['surface_border']} !important;
    border-radius: 14px !important;
}}

[data-testid="stExpander"] summary {{
    font-weight: 600;
    color: {T['text_primary']};
}}

/* ---------------- FOOTER ---------------- */

.app-footer {{
    margin-top: 60px;
    padding: 30px 10px 10px 10px;
    border-top: 1px solid {T['surface_border']};
    text-align: center;
    color: {T['text_muted']};
    font-size: 13px;
}}

.app-footer .foot-brand {{
    font-weight: 700;
    color: {T['text_secondary']};
}}

/* ---------------- MISC ---------------- */

hr {{
    border-color: {T['surface_border']} !important;
}}

::-webkit-scrollbar {{ width: 10px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: {T['accent_a']}55; border-radius: 10px; }}

</style>
""", unsafe_allow_html=True)

# ==========================================================
# STICKY HEADER (rendered via components)
# ==========================================================

col_a, col_b = st.columns([6, 1])
with col_a:
    st.markdown(f"""
    <div class="app-header">
        <div class="brand">
            <div class="brand-badge">✨</div>
            ResumeIQ <span style="color:{T['accent_a']}">AI</span>
        </div>
        <div class="nav-pill">Powered by Gemini</div>
    </div>
    """, unsafe_allow_html=True)

with col_b:
    st.write("")

theme_icon = "🌙" if st.session_state.theme == "dark" else "☀️"
_, tcol = st.columns([9, 1])
with tcol:
    st.button(theme_icon, on_click=toggle_theme, key="theme_toggle", help="Toggle dark / light mode")

# ==========================================================
# HERO
# ==========================================================

st.markdown(f"""
<div class="hero-wrap">
    <div class="hero-eyebrow">⚡ AI-Powered Resume Intelligence</div>
    <div class="hero-title">Your resume, <br/>upgraded by AI.</div>
    <div class="hero-sub">
        Get an instant ATS score, gap analysis, and a personalized roadmap —
        so you walk into every application ready to win.
    </div>
</div>
""", unsafe_allow_html=True)

st.write("")

# ==========================================================
# INPUT SECTION
# ==========================================================

st.markdown('<div class="glass-card">', unsafe_allow_html=True)

st.markdown("""
<div class="section-label">📤 Get Started</div>
<div class="section-caption">Upload your resume and tell us what role you're targeting.</div>
""", unsafe_allow_html=True)

left, right = st.columns([2, 1])

with left:
    uploaded_resume = st.file_uploader(
        "Upload Resume (PDF or DOCX)",
        type=["pdf", "docx"]
    )

with right:
    job_role = st.selectbox(
        "🎯 Target Role",
        [
            "AI Engineer",
            "Machine Learning Engineer",
            "Software Engineer",
            "Data Scientist",
            "Frontend Developer",
            "Backend Developer",
            "Full Stack Developer"
        ]
    )

st.write("")
analyze = st.button("🚀  Analyze Resume")

st.markdown('</div>', unsafe_allow_html=True)

# Lottie-style floating orb placeholder — shown only before an analysis has run
if not analyze and st.session_state.ai_result is None:
    st.markdown(f"""
    <div class="float-orb-wrap">
        <div class="float-orb">🤖</div>
    </div>
    <div class="float-caption">Waiting for your resume — drop a file above to begin the analysis.</div>
    """, unsafe_allow_html=True)

st.write("")

# ==========================================================
# HELPERS — visual components
# ==========================================================

def render_gauge(score: int, accent_a: str, accent_b: str, track: str, text_color: str):
    score = max(0, min(100, score))
    radius = 70
    circumference = 2 * 3.14159265 * radius
    offset = circumference * (1 - score / 100)
    svg = f"""
    <div class="gauge-wrap">
    <svg width="180" height="180" viewBox="0 0 180 180">
        <defs>
            <linearGradient id="gaugeGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="{accent_a}" />
                <stop offset="100%" stop-color="{accent_b}" />
            </linearGradient>
        </defs>
        <circle cx="90" cy="90" r="{radius}" stroke="{track}" stroke-width="14" fill="none"/>
        <circle cx="90" cy="90" r="{radius}" stroke="url(#gaugeGrad)" stroke-width="14" fill="none"
            stroke-dasharray="{circumference}" stroke-dashoffset="{offset}"
            stroke-linecap="round" transform="rotate(-90 90 90)"
            style="transition: stroke-dashoffset 1s ease;"/>
        <text x="90" y="83" text-anchor="middle" class="gauge-value" style="font-size:30px;">{score}</text>
        <text x="90" y="106" text-anchor="middle" class="gauge-value" style="font-size:13px; fill:{text_color}; opacity:0.6;">/ 100</text>
    </svg>
    <div class="gauge-label">ATS Match Score</div>
    </div>
    """
    st.markdown(svg, unsafe_allow_html=True)


def render_progress(label: str, value: int):
    st.markdown(f"""
    <div style="margin-bottom:6px; font-size:14px; font-weight:600; color:{T['text_secondary']};
                display:flex; justify-content:space-between;">
        <span>{label}</span><span>{value}%</span>
    </div>
    <div class="pbar-outer"><div class="pbar-inner" style="width:{value}%;"></div></div>
    """, unsafe_allow_html=True)


def build_report_text(ai_result, job_role):
    lines = []
    lines.append("RESUMEIQ AI — ANALYSIS REPORT")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"Target Role: {job_role}")
    lines.append("=" * 50)
    lines.append(f"\nATS Score: {ai_result.get('ats_score', 'N/A')}/100")
    lines.append(f"Resume Score: {ai_result.get('resume_score', 'N/A')}/100")

    lines.append("\n--- SKILLS FOUND ---")
    for s in ai_result.get("skills_found", []):
        lines.append(f"  + {s}")

    lines.append("\n--- MISSING SKILLS ---")
    for s in ai_result.get("missing_skills", []):
        lines.append(f"  - {s}")

    lines.append("\n--- CAREER RECOMMENDATION ---")
    lines.append(str(ai_result.get("career_recommendation", "N/A")))

    lines.append("\n--- LEARNING ROADMAP ---")
    for i, step in enumerate(ai_result.get("learning_roadmap", []), start=1):
        lines.append(f"  Step {i}: {step}")

    lines.append("\n--- INTERVIEW QUESTIONS ---")
    for i, q in enumerate(ai_result.get("interview_questions", []), start=1):
        lines.append(f"  Q{i}: {q}")

    lines.append("\n--- RESUME IMPROVEMENT SUGGESTIONS ---")
    for s in ai_result.get("resume_suggestions", []):
        lines.append(f"  * {s}")

    return "\n".join(lines)


# ==========================================================
# ANALYZE RESUME  (backend logic unchanged)
# ==========================================================

if analyze:

    if uploaded_resume is None:
        st.error("⚠️ Please upload a PDF or DOCX resume.")
        st.stop()

    with st.spinner("🤖 Gemini AI is analyzing your resume..."):

        time.sleep(1)

        file_type = uploaded_resume.name.split(".")[-1].lower()

        if file_type == "pdf":
            resume_text = extract_pdf_text(uploaded_resume)

        elif file_type == "docx":
            resume_text = extract_docx_text(uploaded_resume)

        else:
            st.error("Unsupported file format.")
            st.stop()

        ai_result = analyze_resume(resume_text, job_role)

    st.session_state.ai_result = ai_result
    st.session_state.resume_text = resume_text

# ==========================================================
# RENDER RESULTS (persists across reruns via session_state)
# ==========================================================

if st.session_state.ai_result is not None:

    ai_result = st.session_state.ai_result

    st.markdown(f"""
    <div style="text-align:center; margin: 10px 0 30px 0; animation: fadeInUp 0.6s ease both;">
        <span style="background:{T['success']}22; color:{T['success']}; padding:10px 22px;
                     border-radius:999px; font-weight:700; font-size:14.5px; border:1px solid {T['success']}44;">
            ✅ Analysis Completed Successfully
        </span>
    </div>
    """, unsafe_allow_html=True)

    # -------------------- SCORE OVERVIEW --------------------

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-label">📊 Score Overview</div>
    <div class="section-caption">How your resume performs against the target role.</div>
    """, unsafe_allow_html=True)

    g1, g2, g3 = st.columns([1, 1, 1])

    with g1:
        render_gauge(int(ai_result["ats_score"]), T["accent_a"], T["accent_b"], T["track"], T["text_primary"])

    with g2:
        st.markdown(f"""
        <div class="stat-card" style="margin-top:20px;">
            <div class="stat-num">{ai_result['resume_score']}</div>
            <div class="stat-title">Resume Score</div>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        render_progress("Resume Quality", int(ai_result["resume_score"]))

    with g3:
        st.markdown(f"""
        <div class="stat-card" style="margin-top:20px;">
            <div class="stat-num">{len(ai_result['skills_found'])}</div>
            <div class="stat-title">Skills Matched</div>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        render_progress("ATS Compatibility", int(ai_result["ats_score"]))

    st.markdown('</div>', unsafe_allow_html=True)
    st.write("")

    # -------------------- SKILLS --------------------

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-label">🧩 Skills Breakdown</div>
    <div class="section-caption">What's already strong, and what's worth adding.</div>
    """, unsafe_allow_html=True)

    sk_left, sk_right = st.columns(2)

    with sk_left:
        st.markdown(f"<div style='font-weight:700; margin-bottom:12px; color:{T['success']};'>✅ Skills Found</div>", unsafe_allow_html=True)
        if ai_result["skills_found"]:
            badges = "".join([f"<span class='badge badge-found'>✓ {s}</span>" for s in ai_result["skills_found"]])
            st.markdown(f"<div class='badge-row'>{badges}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='info-block'>No skills detected.</div>", unsafe_allow_html=True)

    with sk_right:
        st.markdown(f"<div style='font-weight:700; margin-bottom:12px; color:{T['warn']};'>❌ Missing Skills</div>", unsafe_allow_html=True)
        if ai_result["missing_skills"]:
            badges = "".join([f"<span class='badge badge-missing'>+ {s}</span>" for s in ai_result["missing_skills"]])
            st.markdown(f"<div class='badge-row'>{badges}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='info-block'>No missing skills — great match!</div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.write("")

    # -------------------- CAREER RECOMMENDATION --------------------

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-label">💼 Career Recommendation</div>
    <div class="section-caption">Tailored guidance based on your profile.</div>
    """, unsafe_allow_html=True)

    if ai_result["career_recommendation"]:
        st.markdown(f"<div class='info-block'>{ai_result['career_recommendation']}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='info-block'>No career recommendation available.</div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.write("")

    # -------------------- LEARNING ROADMAP (TIMELINE) --------------------

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-label">📚 Learning Roadmap</div>
    <div class="section-caption">Your step-by-step path to close the gap.</div>
    """, unsafe_allow_html=True)

    roadmap = ai_result.get("learning_roadmap", [])

    if roadmap:
        tl_html = "<div class='timeline'>"
        for index, step in enumerate(roadmap, start=1):
            tl_html += f"""
            <div class="tl-item">
                <div class="tl-dot">{index}</div>
                <div class="tl-content">{step}</div>
            </div>
            """
        tl_html += "</div>"
        st.markdown(tl_html, unsafe_allow_html=True)
    else:
        st.markdown("<div class='info-block'>No learning roadmap generated.</div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.write("")

    # -------------------- INTERVIEW QUESTIONS --------------------

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-label">🎤 Interview Questions</div>
    <div class="section-caption">Practice with questions tailored to your target role.</div>
    """, unsafe_allow_html=True)

    questions = ai_result.get("interview_questions", [])

    if questions:
        for i, question in enumerate(questions, start=1):
            with st.expander(f"Question {i}"):
                st.write(question)
    else:
        st.markdown("<div class='info-block'>No interview questions generated.</div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.write("")

    # -------------------- RESUME IMPROVEMENT --------------------

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-label">✨ Resume Improvement Suggestions</div>
    <div class="section-caption">Small changes that make a big difference.</div>
    """, unsafe_allow_html=True)

    suggestions = ai_result.get("resume_suggestions", [])

    if suggestions:
        for suggestion in suggestions:
            st.markdown(f"<div class='suggestion-block'>💡 {suggestion}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='info-block'>No suggestions available.</div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.write("")

    # -------------------- DOWNLOAD REPORT --------------------

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-label">⬇️ Export</div>
    <div class="section-caption">Save a copy of your full analysis.</div>
    """, unsafe_allow_html=True)

    report_text = build_report_text(ai_result, job_role)
    dl1, dl2 = st.columns([1, 1])
    with dl1:
        st.download_button(
            label="📄 Download Report (.txt)",
            data=report_text,
            file_name=f"ResumeIQ_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain"
        )
    with dl2:
        st.download_button(
            label="🗂️ Download Report (.md)",
            data=report_text,
            file_name=f"ResumeIQ_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
            mime="text/markdown"
        )

    st.markdown('</div>', unsafe_allow_html=True)

    st.balloons()

# ==========================================================
# FOOTER
# ==========================================================

st.markdown(f"""
<div class="app-footer">
    <div class="foot-brand">✨ ResumeIQ AI</div>
    <div style="margin-top:6px;">Built with Streamlit &amp; Gemini · Your data is analyzed securely and never stored.</div>
    <div style="margin-top:10px; opacity:0.7;">© {datetime.now().year} ResumeIQ AI. All rights reserved.</div>
</div>
""", unsafe_allow_html=True)