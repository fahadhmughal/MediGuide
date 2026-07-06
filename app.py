import time
import os
import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from chain import build_chain, MODELS

load_dotenv()

st.set_page_config(page_title="MediGuide", page_icon="🩺", layout="centered")

st.markdown(
    """
<style>
:root {
    --app-bg: #f7fafc;
    --panel-bg: #ffffff;
    --text-primary: #0f172a;
    --text-secondary: #334155;
    --text-muted: #64748b;
    --border-color: #e2e8f0;
    --accent: #0f766e;
    --accent-soft: #ecfeff;
    --accent-strong: #0891b2;
    --danger: #dc2626;
    --danger-text: #ffffff;
}

html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stToolbar"] {
    color-scheme: light;
    background-color: var(--app-bg);
    color: var(--text-primary);
}

.stApp {
    background-color: var(--app-bg);
    color: var(--text-primary);
}

.stApp, .stApp p, .stApp li, .stApp label, .stApp span, .stApp div {
    color: var(--text-primary);
}

section[data-testid="stSidebar"] {
    background-color: var(--panel-bg);
    border-right: 1px solid var(--border-color);
    color: var(--text-primary);
}

section[data-testid="stSidebar"] * {
    color: var(--text-primary);
}

section[data-testid="stSidebar"] [data-baseweb="select"],
section[data-testid="stSidebar"] [data-baseweb="select"] * {
    background-color: var(--panel-bg) !important;
    color: var(--text-primary) !important;
}

.stCaption {
    color: var(--text-muted) !important;
}

.stMarkdown {
    color: var(--text-primary);
}

.stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
    color: var(--text-primary);
}

.stButton button,
.stDownloadButton button,
.stSelectbox label,
.stTextInput label,
.stChatInput label {
    color: var(--text-primary) !important;
}

.stButton button {
    background-color: var(--panel-bg);
    border: 1px solid var(--border-color);
}

.stButton button,
.stDownloadButton button {
    color: var(--text-primary) !important;
}

.stButton button:hover,
.stDownloadButton button:hover {
    border-color: var(--accent-strong);
    color: var(--accent-strong) !important;
}

.stSelectbox div[data-baseweb="select"],
.stSelectbox div[data-baseweb="select"] > div,
.stSelectbox div[data-baseweb="select"] input,
.stTextInput input,
.stTextArea textarea,
div[data-testid="stChatInput"] textarea {
    color: var(--text-primary) !important;
    caret-color: var(--text-primary) !important;
    background-color: var(--panel-bg) !important;
}

.stSelectbox div[data-baseweb="select"] *,
.stSelectbox div[data-baseweb="select"] svg {
    color: var(--text-primary) !important;
    fill: var(--text-primary) !important;
}

div[data-baseweb="base-input"],
div[data-baseweb="select"] {
    background-color: var(--panel-bg) !important;
}

div[data-testid="stChatInput"] {
    background-color: var(--panel-bg) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 14px !important;
}

div[data-testid="stChatInput"] textarea {
    background-color: var(--panel-bg) !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder,
div[data-testid="stChatInput"] textarea::placeholder {
    color: var(--text-muted) !important;
}

.stTextInput input,
.stTextArea textarea,
div[data-testid="stChatInput"] textarea,
div[data-baseweb="select"] input {
    -webkit-text-fill-color: var(--text-primary) !important;
}

.stMetric label,
.stMetric div {
    color: var(--text-primary) !important;
}

.disclaimer {
    background-color: var(--accent-soft);
    border: 1px solid #a5f3fc;
    color: var(--accent);
    padding: 12px 16px;
    border-radius: 10px;
    font-size: 14px;
    margin-bottom: 16px;
}

.disclaimer * {
    color: var(--accent);
}

.emergency {
    background-color: var(--danger);
    color: var(--danger-text);
    padding: 16px;
    border-radius: 10px;
    font-weight: 600;
    margin-bottom: 16px;
}

.bubble-user {
    background-color: var(--accent-strong);
    color: #ffffff;
    padding: 10px 16px;
    border-radius: 14px;
    margin: 6px 0;
    max-width: 80%;
    margin-left: auto;
    white-space: pre-wrap;
}

.bubble-user * {
    color: #ffffff;
}

.bubble-bot {
    background-color: var(--panel-bg);
    color: var(--text-secondary);
    padding: 10px 16px;
    border-radius: 14px;
    margin: 6px 0;
    max-width: 80%;
    border: 1px solid var(--border-color);
    white-space: pre-wrap;
}

.bubble-bot * {
    color: var(--text-secondary);
}

/* Streamlit toolbar/header text can inherit dark theme colors; pin it to the light palette. */
[data-testid="stHeader"] *, [data-testid="stToolbar"] * {
    color: var(--text-primary) !important;
}
</style>
""",
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = []
if "stage" not in st.session_state:
    st.session_state.stage = "Gathering Info"
if "stats" not in st.session_state:
    st.session_state.stats = {"calls": 0, "total_tokens": 0, "last_tokens": 0, "last_latency": 0.0}
if "clarifying_intro_shown" not in st.session_state:
    st.session_state.clarifying_intro_shown = False

groq_api_key = os.getenv("GROQ_API_KEY", "").strip()

with st.sidebar:
    st.title("🩺 MediGuide")
    st.caption("AI Symptom-to-Specialist Navigator")
    model_label = st.selectbox("Model", list(MODELS.keys()))
    st.markdown(f"**Stage:** {st.session_state.stage}")

    if st.button("Gather Model Info"):
        s = st.session_state.stats
        st.metric("API calls this session", s["calls"])
        st.metric("Total tokens used", s["total_tokens"])
        st.metric("Last call tokens", s["last_tokens"])
        st.metric("Last response time (s)", round(s["last_latency"], 2))

    if st.button("Reset Conversation"):
        st.session_state.clear()
        st.rerun()

    st.markdown("---")
    st.caption("Not a substitute for professional medical advice. Seek emergency care for urgent symptoms.")

st.title("MediGuide")
st.markdown(
    '<div class="disclaimer">MediGuide does not diagnose conditions. It helps you '
    "identify which specialist to see and what to ask them. Always consult a "
    "licensed physician. If this is an emergency, contact emergency services.</div>",
    unsafe_allow_html=True,
)

for m in st.session_state.messages:
    css_class = "bubble-user" if m["role"] == "user" else "bubble-bot"
    st.markdown(f'<div class="{css_class}">{m["content"]}</div>', unsafe_allow_html=True)

if not groq_api_key:
    st.error(
        "Set GROQ_API_KEY in your environment or .env file to enable AI responses. The app can still load, but chat is disabled until the key is provided."
    )

user_input = st.chat_input("Describe your symptoms...", disabled=not groq_api_key)

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        chain = build_chain(MODELS[model_label])
        start = time.time()
        result = chain.invoke({"input": user_input, "history": st.session_state.history})
        latency = time.time() - start
        parsed = result["parsed"]
        raw = result["raw"]
        usage = getattr(raw, "usage_metadata", None) or {}
        tokens = usage.get("total_tokens", 0)

        s = st.session_state.stats
        s["calls"] += 1
        s["total_tokens"] += tokens
        s["last_tokens"] = tokens
        s["last_latency"] = latency

        if parsed.message_type == "emergency":
            st.session_state.stage = "Emergency"
            display_text = parsed.response_text
        elif parsed.message_type == "clarifying_question":
            st.session_state.stage = "Gathering Info"
            if st.session_state.clarifying_intro_shown:
                display_text = parsed.clarifying_question or parsed.response_text
            else:
                st.session_state.clarifying_intro_shown = True
                if parsed.clarifying_question:
                    display_text = f"{parsed.response_text}\n\n{parsed.clarifying_question}"
                else:
                    display_text = parsed.response_text
        else:
            st.session_state.stage = "Recommendation Ready"
            questions_text = "\n".join(
                f"{i}. {question}" for i, question in enumerate(parsed.appointment_questions or [], 1)
            )
            if questions_text:
                display_text = f"{parsed.response_text}\n\nQuestions to ask your doctor:\n{questions_text}"
            else:
                display_text = f"{parsed.response_text}\n\nQuestions to ask your doctor:\nNo questions were returned."

        st.session_state.history.append(HumanMessage(content=user_input))
        st.session_state.history.append(AIMessage(content=display_text))
        st.session_state.messages.append({"role": "assistant", "content": display_text})

    except Exception as e:
        st.session_state.messages.append(
            {"role": "assistant", "content": f"Sorry, something went wrong reaching the AI service: {e}"}
        )

    st.rerun()
