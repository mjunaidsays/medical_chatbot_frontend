# Medical Chatbot 2.0 - Modern Chat UI

This is an alternative Streamlit frontend for the Medical Chatbot system, designed to look and feel like modern chatbots (e.g., ChatGPT).

## Features
- Chat interface with left/right alignment (bot left, user right)
- Fixed chat input at the bottom
- Exam Bot: Bot asks questions, evaluates, and continues in chat format
- Patient Bot: User asks questions, bot answers in chat format
- Session and topic selection as in the original frontend

## How to Run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the backend (if not already running):
   ```bash
   cd ../backend
   python start_server.py
   ```
3. Run the new frontend:
   ```bash
   streamlit run app.py
   ```

## Note
This UI does not affect the original frontend. Use it for demos or client feedback. 