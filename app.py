import streamlit as st
import requests
import pandas as pd
import time
import io
import base64
from audio_recorder_streamlit import audio_recorder
import uuid

BACKEND_URL = "http://localhost:8000/api/v1"

st.set_page_config(page_title="Medical Chatbot 2.0", page_icon="💬", layout="wide")

# Modern CSS for chat look and sidebar
st.markdown("""
<style>
body {
    background: #fff;
}
.stChatMessage:has(.chat-user) {
    flex-direction: row-reverse;
    text-align: right;
}
.stChatMessage:has(.chat-assistant) {
    flex-direction: row;
    text-align: left;
}
/* Hide the avatar and remove its space completely */
.stChatMessage .avatar {
    display: none !important;
    width: 0 !important;
    min-width: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}
/* Make chat message content and avatar appear side by side */
.stChatMessage {
    flex-direction: row !important;
    align-items: flex-end !important;
}
.stChatMessage:has(.chat-user) {
    flex-direction: row-reverse !important;
    align-items: flex-end !important;
}
.stChatMessage .stMarkdown {
    background: #fff;
    color: #000;
    border-radius: 18px 18px 4px 18px;
    padding: 0.7rem 1.2rem;
    margin: 0.2rem 0;
    max-width: 70%;
    font-size: 1.1rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    display: inline-block;
    border: 1.5px solid #eee;
}
.stChatMessage.user .stMarkdown {
    background: #f5f5f5;
    color: #000;
    border-radius: 18px 18px 18px 4px;
    margin-left: 0;
    border: none;
}
.stChatMessage.assistant .stMarkdown {
    background: #fff;
    color: #000;
    border-radius: 18px 18px 4px 18px;
    margin-right: 0;
    border: 1.5px solid #eee;
}
.stChatInputContainer {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100vw;
    background: #fff;
    box-shadow: 0 -2px 8px rgba(0,0,0,0.04);
    z-index: 100;
    padding: 1rem 0.5rem 0.5rem 0.5rem;
}
/* Button and sidebar color unification */
.stButton > button,
[data-testid="baseButton-secondary"],
[data-testid="baseButton-primary"] {
    border-radius: 18px;
    font-weight: bold;
    background: #f5f5f5 !important;
    color: #000 !important;
    border: 1.5px solid #f5f5f5 !important;
    padding: 0.7rem 1.5rem;
    margin: 0.2rem 0;
    font-size: 1.1rem;
    transition: background 0.2s, border-color 0.2s;
}
.stButton > button:hover, .stButton > button:focus, .stButton > button:active,
[data-testid="baseButton-secondary"]:hover, [data-testid="baseButton-secondary"]:focus, [data-testid="baseButton-secondary"]:active,
[data-testid="baseButton-primary"]:hover, [data-testid="baseButton-primary"]:focus, [data-testid="baseButton-primary"]:active {
    background: #f5f5f5 !important;
    border: 1.5px solid #f5f5f5 !important;
    outline: none !important;
    box-shadow: none !important;
    color: #000 !important;
}
button:focus:not(:active), button:focus:active, button:active {
    border-color: #f5f5f5 !important;
    box-shadow: none !important;
    outline: none !important;
}
.card-hover {
    background: #bdbdbd;
    border: 2px solid #9e9e9e;
    border-radius: 18px;
    padding: 2rem 2.5rem;
    box-shadow: 0 4px 24px rgba(158,158,158,0.12);
    text-align: center;
    transition: background 0.2s, box-shadow 0.2s;
}
.card-hover:hover {
    background: #9e9e9e;
    box-shadow: 0 8px 32px rgba(100,100,100,0.18);
}
.stSelectbox > div {
    border-radius: 12px;
}
.stTextInput > div > input {
    border-radius: 12px;
    padding: 0.7rem 1.2rem;
    font-size: 1.1rem;
}
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    color: #000;
}
/* Sidebar styling */
section[data-testid="stSidebar"] {
    background: #f5f5f5;
    color: #000;
    border-top-right-radius: 24px;
    border-bottom-right-radius: 24px;
    min-width: 270px;
    max-width: 320px;
    border-right: 2px solid #e0e0e0;
}
.sidebar-logo {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 1.5rem;
}
.sidebar-logo img {
    width: 48px;
    height: 48px;
    margin-right: 0.7rem;
    filter: grayscale(1) brightness(0.7);
}
.sidebar-title {
    font-size: 1.5rem;
    font-weight: bold;
    color: #000;
    margin-bottom: 0.5rem;
}
.sidebar-section {
    margin-bottom: 1.5rem;
}
.sidebar-label {
    font-weight: 600;
    color: #000;
    margin-bottom: 0.2rem;
}
.sidebar-value {
    color: #000;
    font-size: 1.1rem;
    margin-bottom: 0.5rem;
}
.sidebar-btn {
    width: 100%;
    margin-bottom: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# Add custom CSS for the End Session button
st.markdown("""
<style>
.end-session-btn {
    background: #f5f5f5 !important;
    color: #000 !important;
    border: 1.5px solid #e0e0e0 !important;
    border-radius: 18px !important;
    font-weight: bold;
    font-size: 1.1rem;
    padding: 0.8rem 1.5rem !important;
    margin: 0.5rem 0 1.2rem 0 !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    transition: background 0.2s, box-shadow 0.2s, transform 0.1s, color 0.2s;
    width: 100%;
    cursor: pointer;
}
.end-session-btn:hover, .end-session-btn:focus {
    background: #e0e0e0 !important;
    box-shadow: 0 4px 16px rgba(0,0,0,0.08);
    transform: translateY(-1px) scale(1.02);
    color: #000 !important;
}
</style>
""", unsafe_allow_html=True)

# Add custom CSS for the send button
st.markdown('''
<style>
.send-btn {
    background: #f5f5f5 !important;
    color: #000 !important;
    border: 1.5px solid #e0e0e0 !important;
    border-radius: 12px !important;
    font-weight: bold;
    font-size: 1.1rem !important;
    width: 70px !important;
    height: 44px !important;
    min-width: 70px !important;
    min-height: 44px !important;
    max-width: 70px !important;
    max-height: 44px !important;
    padding: 0 !important;
    margin: 0 !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.2s, box-shadow 0.2s, transform 0.1s, color 0.2s;
}
.send-btn:hover, .send-btn:focus {
    background: #e0e0e0 !important;
    color: #000 !important;
}
.audio-recorder-streamlit-mic {
    background: #000 !important;
    color: #fff !important;
    border-radius: 12px !important;
    width: 44px !important;
    height: 44px !important;
    min-width: 44px !important;
    min-height: 44px !important;
    max-width: 44px !important;
    max-height: 44px !important;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.3rem !important;
    margin: 0 !important;
    border: none !important;
}
</style>
''', unsafe_allow_html=True)

# Add custom CSS for chat input with send button overlay
st.markdown('''
<style>
.input-send-wrapper {
    position: relative;
    width: 100%;
}
.input-send-wrapper input {
    padding-right: 48px !important;
}
.input-send-btn {
    position: absolute;
    right: 6px;
    top: 50%;
    transform: translateY(-50%);
    background: #f5f5f5 !important;
    color: #000 !important;
    border: none;
    border-radius: 50%;
    font-size: 1.2rem;
    width: 36px;
    height: 36px;
    min-width: 36px;
    min-height: 36px;
    max-width: 36px;
    max-height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: background 0.2s, box-shadow 0.2s, transform 0.1s, color 0.2s;
    z-index: 10;
}
.input-send-btn:hover, .input-send-btn:focus {
    background: #e0e0e0 !important;
    color: #000 !important;
}
</style>
''', unsafe_allow_html=True)

# Add custom CSS for input with send button inside and mic button beside
st.markdown('''
<style>
.input-send-container {
    position: relative;
    width: 100%;
}
.input-send-input {
    width: 100%;
    height: 44px;
    border-radius: 24px;
    border: 2px solid #e57373;
    background: #f5f5f5;
    font-size: 1.1rem;
    padding: 0.7rem 44px 0.7rem 1.2rem;
    box-sizing: border-box;
    outline: none;
    color: #222;
}
.input-send-btn {
    position: absolute;
    right: 8px;
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: none;
    color: #b0b0b0;
    font-size: 1.5rem;
    cursor: pointer;
    padding: 0;
    margin: 0;
    outline: none;
    z-index: 10;
    transition: color 0.2s;
}
.input-send-btn:hover {
    color: #333;
}
.mic-btn {
    background: #000 !important;
    color: #fff !important;
    border-radius: 12px !important;
    width: 44px !important;
    height: 44px !important;
    min-width: 44px !important;
    min-height: 44px !important;
    max-width: 44px !important;
    max-height: 44px !important;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.3rem !important;
    margin: 0 !important;
    border: none !important;
}
</style>
''', unsafe_allow_html=True)

# Add custom CSS for input and button alignment
st.markdown('''
<style>
.input-row .element-container {
    display: flex;
    align-items: center;
    height: 48px;
}
.stTextInput > div > input {
    height: 44px !important;
    border-radius: 12px !important;
    font-size: 1.1rem !important;
    background: #f5f5f5 !important;
}
.send-btn {
    background: #f5f5f5 !important;
    color: #000 !important;
    border: 1.5px solid #e0e0e0 !important;
    border-radius: 12px !important;
    font-weight: bold;
    font-size: 1.1rem !important;
    width: 70px !important;
    height: 44px !important;
    min-width: 70px !important;
    min-height: 44px !important;
    max-width: 70px !important;
    max-height: 44px !important;
    padding: 0 !important;
    margin: 0 !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.2s, box-shadow 0.2s, transform 0.1s, color 0.2s;
}
.send-btn:hover, .send-btn:focus {
    background: #e0e0e0 !important;
    color: #000 !important;
}
.audio-recorder-streamlit-mic {
    background: #000 !important;
    color: #fff !important;
    border-radius: 12px !important;
    width: 44px !important;
    height: 44px !important;
    min-width: 44px !important;
    min-height: 44px !important;
    max-width: 44px !important;
    max-height: 44px !important;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.3rem !important;
    margin: 0 !important;
    border: none !important;
}
</style>
''', unsafe_allow_html=True)

# Add custom CSS for Send button min-width
st.markdown('''
<style>
.send-btn-fixed {
    min-width: 80px !important;
    max-width: 100px !important;
    width: 100% !important;
    font-size: 1.1rem !important;
    font-weight: bold !important;
    padding: 0.7rem 0 !important;
    border-radius: 12px !important;
}
</style>
''', unsafe_allow_html=True)

# Session state initialization
if "page" not in st.session_state:
    st.session_state.page = "bot_select"
if "selected_bot" not in st.session_state:
    st.session_state.selected_bot = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "session_token" not in st.session_state:
    st.session_state.session_token = None
if "available_topics" not in st.session_state:
    st.session_state.available_topics = []
if "selected_topic" not in st.session_state:
    st.session_state.selected_topic = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "exam_finished" not in st.session_state:
    st.session_state.exam_finished = False
if "question_index" not in st.session_state:
    st.session_state.question_index = 0
if "total_questions" not in st.session_state:
    st.session_state.total_questions = 0
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "pending_exam_answer" not in st.session_state:
    st.session_state.pending_exam_answer = None
if "pending_exam_processing" not in st.session_state:
    st.session_state.pending_exam_processing = False

# Add evaluation summary state
if "evaluation_summary" not in st.session_state:
    st.session_state.evaluation_summary = None

# Helper functions
def reset_all():
    for key in [
        "page", "selected_bot", "user_name", "session_token", "available_topics", "selected_topic", "chat_history", "exam_finished", "question_index", "total_questions", "current_question", "pending_exam_answer", "pending_exam_processing", "evaluation_summary", "num_initial_questions", "retry_count", "end_session_triggered", "audio_sent", "voice_transcribed_text"
    ]:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state.page = "bot_select"

def text_to_speech(text):
    """
    Convert text to speech using ElevenLabs API via backend
    """
    try:
        response = requests.post(
            f"{BACKEND_URL}/text-to-speech",
            json={"text": text}
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("audio_base64"):
                # Decode base64 audio
                audio_data = base64.b64decode(data["audio_base64"])
                return audio_data
        return None
    except Exception as e:
        st.error(f"TTS Error: {str(e)}")
        return None

def start_session(bot_type, user_name):
    if bot_type == "exam":
        resp = requests.post(f"{BACKEND_URL}/exam/start_session", json={"user_name": user_name})
    else:
        resp = requests.post(f"{BACKEND_URL}/patient/start_session", json={"user_name": user_name})
    if resp.status_code == 200:
        data = resp.json()
        st.session_state.session_token = data["session_token"]
        st.session_state.available_topics = data["available_topics"]
        st.session_state.user_name = user_name
        st.session_state.selected_bot = bot_type
        return True
    else:
        st.error("Failed to start session.")
        return False

def select_topic(topic, num_questions=None):
    if st.session_state.selected_bot == "exam":
        payload = {"session_token": st.session_state.session_token, "topic": topic}
        if num_questions is not None:
            payload["num_initial_questions"] = int(num_questions)
        resp = requests.post(f"{BACKEND_URL}/exam/select_topic", json=payload)
        if resp.status_code == 200:
            data = resp.json()
            st.session_state.selected_topic = topic
            st.session_state.current_question = data["question"]
            st.session_state.question_index = data["question_index"]
            st.session_state.total_questions = data["total_questions"]
            st.session_state.chat_history = [{"role": "assistant", "content": data["question"]}]
            st.session_state.exam_finished = False
            return True
        else:
            st.error("Failed to select topic.")
            return False
    else:
        resp = requests.post(f"{BACKEND_URL}/patient/select_topic", json={"session_token": st.session_state.session_token, "topic": topic})
        if resp.status_code == 200:
            data = resp.json()
            st.session_state.selected_topic = topic
            st.session_state.current_question = data["question"]
            st.session_state.question_index = data["question_index"]
            st.session_state.total_questions = data["total_questions"]
            st.session_state.chat_history = [{"role": "assistant", "content": data["question"]}]
            st.session_state.exam_finished = False
            return True
        else:
            st.error("Failed to select topic.")
            return False

def submit_exam_answer(answer):
    # Track retries for the current question
    if "retry_count" not in st.session_state:
        st.session_state.retry_count = 0
    # DON'T add to chat history here - it's already done in on_send()
    st.session_state.pending_exam_answer = answer
    st.session_state.pending_exam_processing = False  # Set to False so next rerun just shows spinner
    # Do NOT call st.rerun() here, just return to let UI update
    return

def ask_patient_question(question):
    resp = requests.post(f"{BACKEND_URL}/patient/ask_question", json={"session_token": st.session_state.session_token, "question": question})
    if resp.status_code == 200:
        data = resp.json()
        st.session_state.chat_history.append({"role": "user", "content": question})
        st.session_state.chat_history.append({"role": "assistant", "content": data["answer"]})
        return True
    else:
        st.error("Failed to get answer.")
        return False

def ask_patient_question_direct(question):
    """Direct API call without adding to chat history (already added in on_send)"""
    resp = requests.post(f"{BACKEND_URL}/patient/ask_question", json={"session_token": st.session_state.session_token, "question": question})
    if resp.status_code == 200:
        data = resp.json()
        # Find and replace the most recent __PENDING__ message
        for i in range(len(st.session_state.chat_history)-1, -1, -1):
            if st.session_state.chat_history[i]["role"] == "assistant" and st.session_state.chat_history[i]["content"] == "__PENDING__":
                st.session_state.chat_history[i]["content"] = data["answer"]
                break
        return True
    else:
        # Replace __PENDING__ with error message
        for i in range(len(st.session_state.chat_history)-1, -1, -1):
            if st.session_state.chat_history[i]["role"] == "assistant" and st.session_state.chat_history[i]["content"] == "__PENDING__":
                st.session_state.chat_history[i]["content"] = "[Error: Failed to get answer]"
                break
        st.error("Failed to get answer.")
        return False

# Utility: Process any pending exam answer before ending session

def process_pending_exam_answer():
    # Find the most recent pending assistant message
    for i in range(len(st.session_state.chat_history)-1, -1, -1):
        msg = st.session_state.chat_history[i]
        if msg["role"] == "assistant" and msg["content"] == "__PENDING__":
            answer = st.session_state.pending_exam_answer
            resp = requests.post(f"{BACKEND_URL}/exam/submit_answer", json={
                "session_token": st.session_state.session_token,
                "answer": answer
            })
            if resp.status_code == 200:
                data = resp.json()
                # Remove the pending message
                del st.session_state.chat_history[i]
                # Insert evaluation and next question if present
                eval_text = (
                    data.get("evaluation") or
                    data.get("result") or
                    data.get("feedback") or
                    None
                )
                if eval_text:
                    st.session_state.chat_history.append({"role": "assistant", "content": eval_text})
                else:
                    st.session_state.chat_history.append({"role": "assistant", "content": f"[No evaluation key found. Full response: {data}]"})
                if data.get("next_question"):
                    st.session_state.chat_history.append({"role": "assistant", "content": data["next_question"]})
                # If finished, just set exam_finished flag
                if data.get("finished"):
                    st.session_state.exam_finished = True
                st.session_state.pending_exam_answer = None
                st.session_state.pending_exam_processing = False
                st.rerun()
                break

# Sidebar
with st.sidebar:
    st.markdown('<div class="sidebar-logo"><img src="https://img.icons8.com/color/96/000000/robot-2.png"/><span class="sidebar-title">Medical Chatbot</span></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div class="sidebar-section sidebar-label">Session Info</div>', unsafe_allow_html=True)
    if st.session_state.user_name:
        st.markdown(f'<div class="sidebar-label">User:</div><div class="sidebar-value">{st.session_state.user_name}</div>', unsafe_allow_html=True)
    if st.session_state.selected_bot:
        st.markdown(f'<div class="sidebar-label">Bot:</div><div class="sidebar-value">{st.session_state.selected_bot.title()}</div>', unsafe_allow_html=True)
    if st.session_state.selected_topic:
        st.markdown(f'<div class="sidebar-label">Topic:</div><div class="sidebar-value">{st.session_state.selected_topic}</div>', unsafe_allow_html=True)
    if st.session_state.selected_bot == "exam" and st.session_state.total_questions > 0 and not st.session_state.exam_finished and not st.session_state.evaluation_summary:
        # Use the latest question_index and total_questions from session state
        progress_index = st.session_state.get("question_index", 0) + 1
        progress_total = st.session_state.get("total_questions", 1)
        st.markdown(f'<div class="sidebar-label">Progress:</div><div class="sidebar-value">{progress_index} / {progress_total}</div>', unsafe_allow_html=True)
        # End Session button
        if st.button("End Session", key="sidebar_end_session_btn", help="End the exam and view your evaluation summary"):
            # 1. Process any pending answer before ending session
            for msg in st.session_state.chat_history:
                if msg["role"] == "assistant" and msg["content"] == "__PENDING__":
                    process_pending_exam_answer()
                    st.stop()
            # 2. Now call /exam/end_session
            resp = requests.post(f"{BACKEND_URL}/exam/end_session", json={"session_token": st.session_state.session_token})
            if resp.status_code == 200:
                data = resp.json()
                summary = data.get("evaluation_summary")
                if not summary and ("total_questions" in data and "details" in data):
                    summary = data
                if summary:
                    st.session_state.exam_finished = True
                    st.session_state.evaluation_summary = summary
                    st.session_state.show_eval_summary = True
                    st.session_state.page = "evaluation"
                    st.rerun()
                else:
                    st.error("No evaluation summary returned by backend.")
            elif resp.status_code == 403:
                st.error("You are not authorized to end this session. (403 Forbidden)")
            else:
                st.error("Failed to end session and get evaluation.")
    st.markdown("---")
    # Sidebar navigation buttons
    if st.session_state.page == "chat" and st.session_state.selected_bot == "exam" and not st.session_state.evaluation_summary:
        if st.button("Back to Topic Selection", key="sidebar_back_btn", use_container_width=True):
            st.session_state.page = "topic_select"
            st.rerun()
        if st.button("Reset Session", key="sidebar_reset_btn", use_container_width=True):
            reset_all()
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# UI Pages
def bot_select_page():
    st.markdown("""
    <div style="display: flex; flex-direction: column; align-items: center; margin-top: 2rem;">
        <h1 style="font-size: 2.5rem; color: #000; margin-bottom: 0.5rem;">Welcome to Medical Chatbot</h1>
        <p style="font-size: 1.2rem; color: #000; margin-bottom: 2rem;">Choose your assistant to get started:</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, _ = st.columns([1,1,0.2])
    with col1:
        st.markdown("""
        <div class="card-hover">
            <img src='https://img.icons8.com/ios-filled/100/000000/robot-2.png' width='64'/><br/>
            <span style="font-size: 1.3rem; font-weight: bold; color: #000;">Exam Bot</span><br/>
            <span style="color: #000;">Practice questions, instant feedback, and progress tracking</span><br/>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Exam Bot", key="exam_btn_real", help="Start Exam Bot", use_container_width=True):
            st.session_state.selected_bot = "exam"
            st.session_state.page = "name_input"
            st.rerun()
    with col2:
        st.markdown("""
        <div class="card-hover">
            <img src='https://img.icons8.com/ios-filled/100/000000/doctor-male.png' width='64'/><br/>
            <span style="font-size: 1.3rem; font-weight: bold; color: #000;">Patient Bot</span><br/>
            <span style="color: #000;">Medical information, patient guidance, and Q&amp;A</span><br/>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Patient Bot", key="patient_btn_real", help="Start Patient Bot", use_container_width=True):
            st.session_state.selected_bot = "patient"
            st.session_state.page = "name_input"
            st.rerun()

def name_input_page():
    st.title("👤 Enter Your Name")
    st.markdown("""
    <style>
    .element-container:has(#name-btn-after) + div button:hover {
        background-color: #e0e0e0 !important;
        color: #222 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    user_name = st.text_input("Your Name:", value="" if st.session_state.user_name is None else st.session_state.user_name, key="user_name_input")
    st.markdown('<span id="name-btn-after"></span>', unsafe_allow_html=True)
    col1, col2 = st.columns([1,1], gap="small")
    with col1:
        if st.button("⬅️ Back", key="name_back_btn", use_container_width=True):
            reset_all()
            st.rerun()
    with col2:
        if st.button("Continue", key="name_continue_btn", use_container_width=True):
            if user_name.strip():
                if start_session(st.session_state.selected_bot, user_name.strip()):
                    st.session_state.page = "topic_select"
                    st.rerun()
            else:
                st.warning("Please enter your name.")

def topic_select_page():
    st.title("📚 Select Topic")
    topics = st.session_state.available_topics
    if not topics:
        st.error("No topics available.")
        return
    st.markdown("""
    <style>
    .element-container:has(#topic-btn-after) + div button:hover {
        background-color: #e0e0e0 !important;
        color: #222 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    topic = st.selectbox("Choose a topic:", topics, index=0 if st.session_state.selected_topic is None else topics.index(st.session_state.selected_topic))
    # Add numeric input for number of initial questions (Exam Bot only)
    num_questions = None
    if st.session_state.selected_bot == "exam":
        if "num_initial_questions" not in st.session_state:
            st.session_state.num_initial_questions = 10
        num_questions = st.number_input(
            "How many initial questions do you want to answer?",
            min_value=1, max_value=100, value=st.session_state.num_initial_questions, step=1, key="num_initial_questions_input"
        )
        st.session_state.num_initial_questions = num_questions
    if st.button("Start Chat", use_container_width=True):
        if st.session_state.selected_bot == "exam":
            # Pass number of initial questions to backend
            if select_topic(topic, num_questions):
                st.session_state.page = "chat"
                st.rerun()
        else:
            if select_topic(topic):
                st.session_state.page = "chat"
                st.rerun()
    if st.button("⬅️ Back", use_container_width=True):
        st.session_state.page = "name_input"
        st.rerun()

def chat_page():
    # --- Ensure all session state variables are initialized at the very start ---
    if "input_key" not in st.session_state:
        st.session_state.input_key = 0
    # --- At the start of chat_page(), ensure the flag is initialized ---
    if "input_key" not in st.session_state:
        st.session_state.input_key = 0
    if "chat_input_value" not in st.session_state:
        st.session_state.chat_input_value = ""
    if "voice_transcribed_text" not in st.session_state:
        st.session_state.voice_transcribed_text = ""
    if "last_audio_bytes" not in st.session_state:
        st.session_state.last_audio_bytes = None
    if "pending_exam_submitted" not in st.session_state:
        st.session_state.pending_exam_submitted = False
    # Ensure chat_history is always a list
    if "chat_history" not in st.session_state or not isinstance(st.session_state.chat_history, list):
        st.session_state.chat_history = []
    # --- Topic and Audio Toggle at the very top ---
    col_topic, col_toggle = st.columns([8, 1])
    with col_topic:
        st.title(f"💬 {st.session_state.selected_bot.title()} Chat - {st.session_state.selected_topic}")
    with col_toggle:
        audio_enabled = st.toggle("Audio", value=False, key="audio_toggle")
    st.markdown(f"**User:** {st.session_state.user_name}")
    st.markdown(f"**Session:** {st.session_state.session_token[:8]}...")
    st.markdown("---")
    # Show warning if chat_history is empty
    if not st.session_state.chat_history:
        st.warning("No question received from backend. Please try selecting the topic again.")
    # Display chat history
    pending_typing = False
    for i, msg in enumerate(st.session_state.chat_history):
        if msg["role"] == "user":
            with st.chat_message("user", avatar=None):
                st.markdown(f'<div class="chat-user">{msg["content"]}</div>', unsafe_allow_html=True)
        elif msg["role"] == "assistant" and msg["content"] == "__PENDING__":
            pending_typing = True
        else:
            with st.chat_message("assistant", avatar=None):
                st.markdown(f'<div class="chat-assistant">{msg["content"]}</div>', unsafe_allow_html=True)
                # Only show speaker button if audio is enabled
                if msg["role"] == "assistant" and msg["content"] != "__PENDING__" and st.session_state.get("audio_toggle", False):
                    speaker_key = f"speaker_btn_{i}"
                    col1, col2 = st.columns([1, 20])
                    with col1:
                        if st.button("🔊", key=speaker_key, help="Listen to this message"):
                            audio_data = text_to_speech(msg["content"])
                            if audio_data:
                                b64 = base64.b64encode(audio_data).decode()
                                unique_id = uuid.uuid4()
                                audio_html = f'''
                                    <audio autoplay style="display:none;" id="audio_{unique_id}">
                                        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3" />
                                    </audio>
                                '''
                                st.markdown(audio_html, unsafe_allow_html=True)
                            else:
                                st.error("Failed to generate audio")
                    with col2:
                        st.write("")  # Empty space for alignment
    # Show typing animation if pending
    if pending_typing:
        with st.chat_message("assistant", avatar=None):
            placeholder = st.empty()
            import time
            for i in range(12):
                dots = "." * ((i % 3) + 1)
                placeholder.markdown(f"<span style='font-size:1.2rem;'>" + dots + "</span>", unsafe_allow_html=True)
                time.sleep(0.17)

    # --- Modern chat input row using streamlit_chat_widget pinned to bottom ---
    st.markdown("""
    <style>
    body {
        background: linear-gradient(90deg, #a8e063 0%, #56c6e6 100%);
    }
    </style>
    """, unsafe_allow_html=True)
    # --- Chat input row with audio recorder and send button overlay ---
    def on_send():
        # Get current input key and read from the correct widget
        current_input_key = f"chat_input_box_{st.session_state.input_key}"
        user_input = st.session_state.get(current_input_key, "")
        
        if user_input and user_input.strip():
            # Display the user's message immediately
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            # Show loading dots in place of bot response
            st.session_state.chat_history.append({"role": "assistant", "content": "__PENDING__"})
            
            # Clear voice input after use
            st.session_state.voice_transcribed_text = ""
            
            if st.session_state.selected_bot == "exam":
                # For exam bot, set pending answer for processing
                st.session_state.pending_exam_answer = user_input
                st.session_state.pending_exam_processing = False
                st.session_state.pending_exam_submitted = False  # Reset flag to trigger backend call on next rerun
            else:
                # For patient bot, trigger direct API call
                ask_patient_question_direct(user_input)
            
            # Increment the input key to force widget recreation and clearing
            st.session_state.input_key += 1
            # Reset the chat input value for next input
            st.session_state.chat_input_value = ""
            # Do NOT call st.rerun() here; Streamlit reruns automatically after callback

    # Update chat_input_value based on voice input
    if st.session_state.voice_transcribed_text:
        st.session_state.chat_input_value = st.session_state.voice_transcribed_text
    
    # Create dynamic input key for clearing
    input_key = f"chat_input_box_{st.session_state.input_key}"
    
    col1, col2, col3 = st.columns([10, 1.5, 1.5], gap="small")
    with col1:
        st.text_input(
            label="Message",  # Non-empty label for accessibility
            value=st.session_state.chat_input_value,
            key=input_key,
            placeholder="Type a message...",
            label_visibility="collapsed"  # Hide label visually, removed on_change to fix double submission
        )
    with col2:
        audio_bytes = None
        if st.session_state.get("audio_toggle", False):
            audio_bytes = audio_recorder(
                text="",
                icon_size="2x",
                pause_threshold=2.0,
                sample_rate=16000,
                key="audio_recorder_btn"
            )
    with col3:
        # Only trigger on_send if the input is not empty and not just whitespace
        if st.button("Send", key="send_btn", use_container_width=True):
            user_input = st.session_state.get(input_key, "")
            if user_input and user_input.strip():
                on_send()
        # Apply fixed style to the button
        st.markdown('<style>div[data-testid="column"] button[kind="primary"] {min-width:80px !important; max-width:100px !important; width:100% !important;}</style>', unsafe_allow_html=True)
    # --- Show warning if last transcription failed ---
    if st.session_state.get("show_transcription_warning"):
        st.warning("No transcript returned by backend.")
        st.session_state.show_transcription_warning = False
    # Only call speech-to-text if new audio is recorded (not on every rerun)
    if audio_bytes and (st.session_state.last_audio_bytes != audio_bytes):
        files = {"file": ("audio.wav", audio_bytes, "audio/wav")}
        try:
            resp = requests.post(f"{BACKEND_URL}/speech-to-text/", files=files)
            if resp.status_code == 200:
                data = resp.json()
                transcript = data.get("text") or data.get("transcript")
                if transcript and transcript.strip():
                    st.session_state.voice_transcribed_text = transcript
                    st.session_state.show_transcription_warning = False
                    st.session_state.chat_input_value = transcript  # This is before the widget is created on next rerun
                else:
                    st.session_state.show_transcription_warning = True
            else:
                st.session_state.show_transcription_warning = True
        except Exception as e:
            st.session_state.show_transcription_warning = True
        # Always update last_audio_bytes after processing
        st.session_state.last_audio_bytes = audio_bytes
        if "audio_recorder_btn" in st.session_state:
            del st.session_state["audio_recorder_btn"]
        st.rerun()
    # --- Exam bot backend processing (separate rerun approach) ---
    if st.session_state.selected_bot == "exam":
        # Check if we have a pending answer that hasn't been processed yet
        if st.session_state.get("pending_exam_answer") and not st.session_state.get("pending_exam_submitted", False):
            # Set a flag to trigger backend processing in next rerun
            st.session_state.pending_exam_submitted = True
            # Immediately rerun to show the UI update first
            st.rerun()
        
        # In a separate rerun, do the actual backend processing
        if st.session_state.get("pending_exam_answer") and st.session_state.get("pending_exam_submitted", False) and not st.session_state.get("backend_processing_done", False):
            # Mark processing as started to prevent duplicate calls
            st.session_state.backend_processing_done = True
            
            answer = st.session_state.pending_exam_answer
            resp = requests.post(f"{BACKEND_URL}/exam/submit_answer", json={
                "session_token": st.session_state.session_token,
                "answer": answer
            })
            
            # Find and replace the __PENDING__ message
            for i in range(len(st.session_state.chat_history)-1, -1, -1):
                msg = st.session_state.chat_history[i]
                if msg["role"] == "assistant" and msg["content"] == "__PENDING__":
                    if resp.status_code == 200:
                        data = resp.json()
                        with st.expander("DEBUG: Backend response for exam/submit_answer"):
                            st.json(data)
                        print("DEBUG: Backend response for exam/submit_answer:", data)
                        # Remove the pending message
                        del st.session_state.chat_history[i]
                        # Update question index and total questions if present
                        if "question_index" in data:
                            st.session_state.question_index = data["question_index"]
                        if "total_questions" in data:
                            st.session_state.total_questions = data["total_questions"]
                        # Insert evaluation and next question if present
                        eval_text = (
                            data.get("evaluation") or
                            data.get("result") or
                            data.get("feedback") or
                            None
                        )
                        if eval_text:
                            st.session_state.chat_history.append({"role": "assistant", "content": eval_text})
                        else:
                            st.session_state.chat_history.append({"role": "assistant", "content": f"[No evaluation key found. Full response: {data}]"})
                        if data.get("next_question"):
                            st.session_state.chat_history.append({"role": "assistant", "content": data["next_question"]})
                        # If finished, just set exam_finished flag
                        if data.get("finished"):
                            st.session_state.exam_finished = True
                            # Do NOT call end_session or rerun here!
                    else:
                        del st.session_state.chat_history[i]
                        # Only show error if backend actually returns an error
                        st.session_state.chat_history.append({"role": "assistant", "content": "[Error: Failed to get evaluation]"})
                    break
            
            # Clean up pending state
            st.session_state.pending_exam_answer = None
            st.session_state.pending_exam_processing = False
            st.session_state.pending_exam_submitted = False
            st.session_state.backend_processing_done = False
            st.rerun()
# After processing all questions and receiving exam_finished/evaluation_summary
    if st.session_state.selected_bot == "exam" and st.session_state.get("exam_finished") and not st.session_state.get("evaluation_summary"):
        st.success("You have completed all questions!")
        if st.button("Show Evaluation Summary", key="show_eval_summary_btn", use_container_width=True):
            # 1. Process any pending answer before ending session
            for msg in st.session_state.chat_history:
                if msg["role"] == "assistant" and msg["content"] == "__PENDING__":
                    process_pending_exam_answer()
                    st.stop()
            # 2. Now call /exam/end_session
            resp = requests.post(f"{BACKEND_URL}/exam/end_session", json={"session_token": st.session_state.session_token})
            if resp.status_code == 200:
                data = resp.json()
                with st.expander("DEBUG: Backend response for exam/end_session"):
                    st.json(data)
                summary = data.get("evaluation_summary")
                if not summary and ("total_questions" in data and "details" in data):
                    summary = data
                if summary:
                    st.session_state["evaluation_summary"] = summary
                    st.session_state["show_eval_summary"] = True
                    st.session_state.page = "evaluation"
                    st.rerun()
                else:
                    st.error("No evaluation summary returned by backend.")
            elif resp.status_code == 403:
                st.error("You are not authorized to end this session. (403 Forbidden)")
            else:
                st.error("Failed to end session and get evaluation.")
        st.stop()
    elif st.session_state.selected_bot == "exam" and st.session_state.get("evaluation_summary"):
        st.header("Evaluation Summary")
        st.markdown(st.session_state["evaluation_summary"])
        st.stop()
    # Optional: Add a little CSS for mic button alignment
    st.markdown("""
        <style>
        button[kind="secondary"] {
            font-size: 1.5rem !important;
            padding: 0.3rem 0.7rem !important;
            border-radius: 50% !important;
            margin-top: 0.2rem !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Add CSS for speaker button styling
    st.markdown("""
    <style>
    /* Speaker button styling */
    .speaker-btn {
        background: #f0f0f0 !important;
        color: #333 !important;
        border: 1px solid #ddd !important;
        border-radius: 50% !important;
        width: 40px !important;
        height: 40px !important;
        font-size: 16px !important;
        padding: 0 !important;
        margin: 5px 0 !important;
        transition: all 0.2s ease !important;
    }
    .speaker-btn:hover {
        background: #e0e0e0 !important;
        transform: scale(1.1) !important;
    }
    /* Audio player styling */
    .stAudio {
        margin-top: 10px !important;
        margin-bottom: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    # --- End Speech to Text Integration ---

# Evaluation summary page

def evaluation_page():
    summary = st.session_state.evaluation_summary
    if not summary:
        st.error("No evaluation summary available.")
        return
    st.title("\U0001F4CA Exam Evaluation Summary")
    st.markdown(f"**Total Questions:** {summary['total_questions']}")
    st.markdown(f"**Correct Answers:** {summary['correct_count']}")
    st.markdown(f"**Wrong Answers:** {summary['wrong_count']}")
    percent = 0
    if summary['total_questions'] > 0:
        percent = (summary['correct_count'] / summary['total_questions']) * 100
    # Determine result category
    if percent <= 50:
        result = "Fail"
    elif 60 <= percent <= 69:
        result = "Pass"
    elif 70 <= percent <= 79:
        result = "Good Pass"
    elif percent >= 80:
        result = "Excellent"
    else:
        result = "Fail"
    st.markdown(f"**Overall Result:** <span style='font-size:1.2rem; font-weight:bold;'>{result}</span>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### Details:")
    # Build HTML for download
    html_summary = f"""
    <h1>Exam Evaluation Summary</h1>
    <p><b>Total Questions:</b> {summary['total_questions']}</p>
    <p><b>Correct Answers:</b> {summary['correct_count']}</p>
    <p><b>Wrong Answers:</b> {summary['wrong_count']}</p>
    <p><b>Overall Result:</b> <span style='font-size:1.2rem; font-weight:bold;'>{result}</span></p>
    <hr/>
    <h2>Details:</h2>
    """
    for idx, detail in enumerate(summary['details']):
        st.markdown(f"**Q{idx+1}:** {detail['question']}")
        st.markdown(f"- Your Answer: {detail['your_answer']}")
        st.markdown(f"- Actual Answer: {detail.get('actual_answer', '[Not available]')}")
        st.markdown(f"- Result: <span style='color:{'green' if detail['result']=='Correct' else 'red'};'>{detail['result']}</span>", unsafe_allow_html=True)
        st.markdown(f"- Feedback: {detail.get('feedback', '[No feedback]')}")
        st.markdown("---")
        html_summary += f"""
        <div style='margin-bottom:16px;'>
        <b>Q{idx+1}:</b> {detail['question']}<br/>
        <b>Your Answer:</b> {detail['your_answer']}<br/>
        <b>Actual Answer:</b> {detail.get('actual_answer', '[Not available]')}<br/>
        <b>Result:</b> <span style='color:{'green' if detail['result']=='Correct' else 'red'};'>{detail['result']}</span><br/>
        <b>Feedback:</b> {detail.get('feedback', '[No feedback]')}<br/>
        </div>
        <hr/>
        """
    # Advanced: Download summary as PDF
    import requests as req
    from io import BytesIO
    # Show the download button directly, styled like Start New Session
    if st.button("Download Summary as PDF", use_container_width=True, key="download_pdf_btn", type="primary"):
        # Call backend to get PDF
        resp = req.post(f"{BACKEND_URL}/exam/evaluation_pdf", json={"session_token": st.session_state.session_token})
        if resp.status_code == 200:
            pdf_bytes = resp.content
            st.download_button(
                label="Click here to download PDF",
                data=pdf_bytes,
                file_name="evaluation_summary.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="pdf_download_btn_real"
            )
        else:
            st.error("Failed to generate PDF. Please try again.")
    if st.button("Start New Session", use_container_width=True):
        reset_all()
        st.rerun()

# Page routing
if st.session_state.page == "bot_select":
    bot_select_page()
elif st.session_state.page == "name_input":
    name_input_page()
elif st.session_state.page == "topic_select":
    topic_select_page()
elif st.session_state.page == "chat":
    chat_page()
elif st.session_state.page == "evaluation":
    evaluation_page() 