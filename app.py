import streamlit as st
import requests
import pandas as pd
import time

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

# Helper functions
def reset_all():
    for key in ["page", "selected_bot", "user_name", "session_token", "available_topics", "selected_topic", "chat_history", "exam_finished", "question_index", "total_questions", "current_question", "pending_exam_answer", "pending_exam_processing"]:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state.page = "bot_select"

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

def select_topic(topic):
    if st.session_state.selected_bot == "exam":
        resp = requests.post(f"{BACKEND_URL}/exam/select_topic", json={"session_token": st.session_state.session_token, "topic": topic})
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
            st.session_state.selected_topic = topic
            st.session_state.chat_history = []
            return True
        else:
            st.error("Failed to select topic.")
            return False

def submit_exam_answer(answer):
    # Track retries for the current question
    if "retry_count" not in st.session_state:
        st.session_state.retry_count = 0
    # Immediately show user answer and pending bot message
    st.session_state.chat_history.append({"role": "user", "content": answer})
    st.session_state.chat_history.append({"role": "assistant", "content": "__PENDING__"})
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
    if st.session_state.selected_bot == "exam" and st.session_state.total_questions > 0:
        st.markdown(f'<div class="sidebar-label">Progress:</div><div class="sidebar-value">{st.session_state.question_index + 1} / {st.session_state.total_questions}</div>', unsafe_allow_html=True)
    st.markdown("---")
    if st.session_state.page == "chat":
        if st.button("Back to Topic Selection", key="sidebar_back", use_container_width=True):
            st.session_state.page = "topic_select"
            st.rerun()
        if st.button("Reset Session", key="sidebar_reset", use_container_width=True):
            reset_all()
            st.rerun()

# UI Pages
def bot_select_page():
    st.markdown("""
    <div style="display: flex; flex-direction: column; align-items: center; margin-top: 2rem;">
        <h1 style="font-size: 2.5rem; color: #000; margin-bottom: 0.5rem;">Welcome to Medical Chatbot 2.0</h1>
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
    name = st.text_input("Your Name:", value="" if st.session_state.user_name is None else st.session_state.user_name)
    if st.button("Continue", use_container_width=True):
        if name.strip():
            if start_session(st.session_state.selected_bot, name.strip()):
                st.session_state.page = "topic_select"
                st.rerun()
        else:
            st.error("Please enter your name.")
    if st.button("⬅️ Back", use_container_width=True):
        reset_all()
        st.rerun()

def topic_select_page():
    st.title("📚 Select Topic")
    topics = st.session_state.available_topics
    if not topics:
        st.error("No topics available.")
        return
    topic = st.selectbox("Choose a topic:", topics, index=0 if st.session_state.selected_topic is None else topics.index(st.session_state.selected_topic))
    if st.button("Start Chat", use_container_width=True):
        if select_topic(topic):
            st.session_state.page = "chat"
            st.rerun()
    if st.button("⬅️ Back", use_container_width=True):
        st.session_state.page = "name_input"
        st.rerun()

def chat_page():
    st.title(f"💬 {st.session_state.selected_bot.title()} Chat - {st.session_state.selected_topic}")
    st.markdown(f"**User:** {st.session_state.user_name}")
    st.markdown(f"**Session:** {st.session_state.session_token[:8]}...")
    st.markdown("---")
    # Display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            # Add a hidden span for CSS targeting
            if msg["role"] == "user":
                st.markdown("<span class='chat-user'></span>", unsafe_allow_html=True)
            else:
                st.markdown("<span class='chat-assistant'></span>", unsafe_allow_html=True)
            st.markdown(msg["content"])
    # Chat input at bottom
    if st.session_state.selected_bot == "exam":
        if st.session_state.exam_finished:
            st.success("🎉 Exam completed! You can start a new session.")
            if st.button("Start New Session", use_container_width=True):
                reset_all()
                st.rerun()
        else:
            # Only show input if not waiting for bot response
            if not st.session_state.get("pending_exam_processing", False):
                user_input = st.chat_input("Type your answer and press Enter...")
                if user_input:
                    st.session_state.chat_history.append({"role": "user", "content": user_input})
                    st.session_state.pending_exam_processing = True
                    st.session_state.pending_exam_answer = user_input
                    st.rerun()
            # If waiting for bot response, show loading animation and process
            elif st.session_state.get("pending_exam_processing", False) and st.session_state.get("pending_exam_answer"):
                with st.chat_message("assistant"):
                    placeholder = st.empty()
                    for i in range(24):  # ~4 seconds animation
                        dots = "." * ((i % 3) + 1)
                        placeholder.markdown(f"<span style='font-size:1.2rem;'>" + dots + "</span>", unsafe_allow_html=True)
                        time.sleep(0.17)
                    resp = requests.post(f"{BACKEND_URL}/exam/submit_answer", json={
                        "session_token": st.session_state.session_token,
                        "answer": st.session_state.pending_exam_answer,
                        "retry_count": st.session_state.get("retry_count", 0)
                    })
                    if resp.status_code == 200:
                        data = resp.json()
                        if data["feedback"] == "Bad" and data["correct_answer"] is None:
                            st.session_state.retry_count = st.session_state.get("retry_count", 0) + 1
                            feedback = "Your answer was incorrect, please try again."
                            placeholder.markdown(feedback)
                            st.session_state.chat_history.append({"role": "assistant", "content": feedback})
                        elif data["feedback"] == "Bad" and data["correct_answer"] is not None:
                            st.session_state.chat_history.append({"role": "assistant", "content": "You don't know the answer to this question."})
                            feedback = f"**Correct Answer:** {data['correct_answer']}"
                            placeholder.markdown(feedback)
                            st.session_state.chat_history.append({"role": "assistant", "content": feedback})
                            st.session_state.retry_count = 0
                        else:
                            feedback = f"**Evaluation:** {data['feedback']}\n\n**Correct Answer:** {data['correct_answer']}"
                            placeholder.markdown(feedback)
                            st.session_state.chat_history.append({"role": "assistant", "content": feedback})
                            st.session_state.retry_count = 0
                        if not data["finished"]:
                            st.session_state.current_question = data["next_question"]
                            st.session_state.question_index = data["question_index"]
                            if data["next_question"] is not None:
                                st.session_state.chat_history.append({"role": "assistant", "content": data["next_question"]})
                        else:
                            st.session_state.exam_finished = True
                            st.session_state.current_question = None
                    else:
                        placeholder.markdown("[Error: Failed to submit answer]")
                        st.session_state.chat_history.append({"role": "assistant", "content": "[Error: Failed to submit answer]"})
                    # Reset pending state
                    st.session_state.pending_exam_processing = False
                    st.session_state.pending_exam_answer = None
                    st.rerun()
    else:
        user_input = st.chat_input("Ask a question about the selected topic...")
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)
            with st.chat_message("assistant"):
                placeholder = st.empty()
                for i in range(12):  # ~2 seconds animation
                    dots = "." * ((i % 3) + 1)
                    placeholder.markdown(f"<span style='font-size:1.2rem;'>" + dots + "</span>", unsafe_allow_html=True)
                    time.sleep(0.17)
                resp = requests.post(f"{BACKEND_URL}/patient/ask_question", json={
                    "session_token": st.session_state.session_token,
                    "question": user_input
                })
                if resp.status_code == 200:
                    data = resp.json()
                    placeholder.markdown(data["answer"])
                    st.session_state.chat_history.append({"role": "assistant", "content": data["answer"]})
                else:
                    placeholder.markdown("[Error: Failed to get answer]")
                    st.session_state.chat_history.append({"role": "assistant", "content": "[Error: Failed to get answer]"})
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