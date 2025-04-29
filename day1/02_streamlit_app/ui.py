import streamlit as st
import pandas as pd
from database import save_to_db, get_chat_history, get_db_count, clear_db
from llm import generate_response
from data import create_sample_evaluation_data
from metrics import get_metrics_descriptions

st.markdown("""
    <style>
        .main {
            background-color: #ffffff;
        }
        .chat-box {
            background: linear-gradient(135deg, #f0f4f8, #d9e2ec);
            padding: 20px;
            border-radius: 20px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .chat-box:hover {
            transform: scale(1.02);
        }
        .feedback-area textarea {
            background-color: #f9f9f9 !important;
            border-radius: 10px;
        }
        .custom-button button {
            background-color: #ff6d01;
            color: white;
            border-radius: 10px;
            padding: 10px;
        }
        .custom-button button:hover {
            background-color: #ff8533;
        }
    </style>
""", unsafe_allow_html=True)


def display_chat_page(pipe):
    st.markdown("<div class='chat-box'>", unsafe_allow_html=True)
    st.subheader("\U0001F4AC Chat with Gemma")
    user_question = st.text_area("質問をどうぞ", key="question_input", height=100, value=st.session_state.get("current_question", ""))
    submit_button = st.button("\U0001F680 質問を送信", key="submit_button")

    if "current_question" not in st.session_state:
        st.session_state.current_question = ""
    if "current_answer" not in st.session_state:
        st.session_state.current_answer = ""
    if "response_time" not in st.session_state:
        st.session_state.response_time = 0.0
    if "feedback_given" not in st.session_state:
        st.session_state.feedback_given = False

    if submit_button and user_question:
        st.session_state.current_question = user_question
        st.session_state.current_answer = ""
        st.session_state.feedback_given = False

        with st.spinner("\U0001F916 モデルが考え中..."):
            answer, response_time = generate_response(pipe, user_question)
            st.session_state.current_answer = answer
            st.session_state.response_time = response_time
            st.rerun()

    if st.session_state.current_question and st.session_state.current_answer:
        st.markdown("---")
        st.subheader("\U0001F4DD モデルの回答")
        st.markdown(st.session_state.current_answer)
        st.info(f"応答時間: {st.session_state.response_time:.2f} 秒")

        if not st.session_state.feedback_given:
            display_feedback_form()
        else:
            if st.button("\U0001F501 次の質問へ", key="next_question"):
                st.session_state.current_question = ""
                st.session_state.current_answer = ""
                st.session_state.response_time = 0.0
                st.session_state.feedback_given = False
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def display_feedback_form():
    with st.form("feedback_form"):
        st.markdown("<div class='feedback-area'>", unsafe_allow_html=True)
        st.subheader("\U0001F4AC フィードバックをお願いします")
        feedback = st.radio("評価を選んでください", ["正確", "部分的に正確", "不正確"], key="feedback_radio", horizontal=True)
        correct_answer = st.text_area("正しいと思われる回答（任意）", key="correct_answer_input", height=100)
        feedback_comment = st.text_area("コメント（任意）", key="feedback_comment_input", height=100)
        submitted = st.form_submit_button("\U0001F4E4 フィードバックを送信")
        st.markdown("</div>", unsafe_allow_html=True)

        if submitted:
            is_correct = 1.0 if feedback == "正確" else (0.5 if feedback == "部分的に正確" else 0.0)
            combined_feedback = feedback + (f": {feedback_comment}" if feedback_comment else "")

            save_to_db(
                st.session_state.current_question,
                st.session_state.current_answer,
                combined_feedback,
                correct_answer,
                is_correct,
                st.session_state.response_time
            )
            st.session_state.feedback_given = True
            st.success("\u2705 フィードバックが保存されました！")
            st.rerun()
