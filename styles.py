"""
Finance Bro — Styles
----------------------
All custom CSS lives here as a single string, injected once via st.markdown.
Design language: dark mode, glassmorphism, neon-gradient accents, rounded corners.
"""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap');

:root {
    --bro-bg: #0b0e17;
    --bro-bg-alt: #11141f;
    --bro-purple: #8b5cf6;
    --bro-pink: #ec4899;
    --bro-green: #22d3a5;
    --bro-yellow: #fbbf24;
    --bro-red: #f87171;
    --bro-blue: #60a5fa;
    --glass-bg: rgba(255, 255, 255, 0.05);
    --glass-border: rgba(255, 255, 255, 0.12);
}

/* ---------- global ---------- */
html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: radial-gradient(circle at 15% 0%, #1a1030 0%, var(--bro-bg) 45%),
                radial-gradient(circle at 85% 100%, #0d2233 0%, var(--bro-bg) 55%),
                var(--bro-bg);
    color: #f5f5f7;
}

h1, h2, h3, h4 {
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
}

/* hide default streamlit chrome */
#MainMenu, footer, header {visibility: hidden;}
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1100px;
}

/* ---------- hero / gradient text ---------- */
.bro-gradient-text {
    background: linear-gradient(90deg, var(--bro-purple), var(--bro-pink) 55%, var(--bro-yellow));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 800;
}

.bro-hero {
    padding: 28px 32px;
    border-radius: 28px;
    background: linear-gradient(135deg, rgba(139,92,246,0.25), rgba(236,72,153,0.18));
    border: 1px solid var(--glass-border);
    margin-bottom: 22px;
    backdrop-filter: blur(14px);
}

/* ---------- glass cards ---------- */
.glass-card {
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    border-radius: 22px;
    padding: 22px 24px;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.35);
    margin-bottom: 16px;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.glass-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(0,0,0,0.45);
}

.metric-card {
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    border-radius: 20px;
    padding: 18px 20px;
    text-align: left;
    backdrop-filter: blur(14px);
}
.metric-label {
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #a1a1aa;
    margin-bottom: 6px;
}
.metric-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.7rem;
    font-weight: 700;
    color: #ffffff;
}
.metric-sub {
    font-size: 0.78rem;
    color: #8b8b96;
    margin-top: 4px;
}

/* ---------- badges / pills ---------- */
.pill {
    display: inline-block;
    padding: 5px 14px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
    margin-right: 6px;
    margin-bottom: 6px;
}
.pill-green { background: rgba(34,211,165,0.18); color: var(--bro-green); border: 1px solid rgba(34,211,165,0.4); }
.pill-yellow { background: rgba(251,191,36,0.18); color: var(--bro-yellow); border: 1px solid rgba(251,191,36,0.4); }
.pill-red { background: rgba(248,113,113,0.18); color: var(--bro-red); border: 1px solid rgba(248,113,113,0.4); }
.pill-purple { background: rgba(139,92,246,0.2); color: #c4b5fd; border: 1px solid rgba(139,92,246,0.45); }

/* ---------- verdict banner ---------- */
.verdict-box {
    border-radius: 24px;
    padding: 26px 28px;
    text-align: center;
    backdrop-filter: blur(14px);
    border: 1px solid var(--glass-border);
    margin: 18px 0;
}
.verdict-score {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    margin: 0;
}
.verdict-label {
    font-size: 1.1rem;
    font-weight: 600;
    margin-top: 4px;
    letter-spacing: 0.02em;
}

/* ---------- badge tiles for gamification ---------- */
.badge-tile {
    border-radius: 18px;
    padding: 16px;
    text-align: center;
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
}
.badge-tile .emoji { font-size: 2.2rem; }
.badge-tile.locked { opacity: 0.35; filter: grayscale(1); }

/* ---------- streak flame ---------- */
.streak-count {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.4rem;
    font-weight: 800;
}

/* ---------- chat bubbles ---------- */
.chat-bubble-user {
    background: linear-gradient(135deg, var(--bro-purple), var(--bro-pink));
    color: white;
    padding: 10px 16px;
    border-radius: 18px 18px 4px 18px;
    margin: 6px 0;
    max-width: 80%;
    margin-left: auto;
    font-size: 0.92rem;
}
.chat-bubble-bro {
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    color: #f5f5f7;
    padding: 10px 16px;
    border-radius: 18px 18px 18px 4px;
    margin: 6px 0;
    max-width: 80%;
    font-size: 0.92rem;
}

/* ---------- buttons ---------- */
div.stButton > button, div.stFormSubmitButton > button {
    background: linear-gradient(135deg, var(--bro-purple), var(--bro-pink));
    color: white;
    border: none;
    border-radius: 14px;
    padding: 0.55rem 1.4rem;
    font-weight: 600;
    transition: transform 0.12s ease, box-shadow 0.12s ease;
    box-shadow: 0 4px 14px rgba(139,92,246,0.35);
}
div.stButton > button:hover, div.stFormSubmitButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 20px rgba(139,92,246,0.45);
    color: white;
}

/* secondary style buttons */
div.stButton > button[kind="secondary"] {
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    box-shadow: none;
}

/* ---------- inputs ---------- */
.stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
    border-radius: 12px !important;
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid var(--glass-border) !important;
    color: #f5f5f7 !important;
}

/* ---------- sidebar ---------- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0f1a 0%, #0b0e17 100%);
    border-right: 1px solid var(--glass-border);
}

/* ---------- radio nav as pills ---------- */
div[role="radiogroup"] label {
    border-radius: 12px;
    padding: 4px 2px;
}

hr {
    border-color: var(--glass-border) !important;
}

/* progress bar accent */
div[data-testid="stProgress"] > div > div > div {
    background-image: linear-gradient(90deg, var(--bro-purple), var(--bro-pink));
}
</style>
"""


def inject_css(st):
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def metric_card_html(label, value, sub=""):
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-sub">{sub}</div>
    </div>
    """


def pill_html(text, kind="purple"):
    return f'<span class="pill pill-{kind}">{text}</span>'
