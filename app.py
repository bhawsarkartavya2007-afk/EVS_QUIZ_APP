import streamlit as st
import pandas as pd
import random
import base64
import os

# 1. Background setup
def add_bg(image_file):
    if os.path.exists(image_file):
        with open(image_file, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url(data:image/png;base64,{encoded});
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}
            p, div, label, h1, h2, h3 {{ color: black !important; font-weight: bold; }}
            </style>
            """, unsafe_allow_html=True
        )

# 2. Session State Initialization
if 'step' not in st.session_state: st.session_state.step = "start"
if 'questions' not in st.session_state:
    df = pd.read_excel("quiz_data.xlsx")
    # Yahan tumhare column ke naam use kiye hain
    st.session_state.questions = df.sample(20).to_dict('records')

# 3. App Flow
if st.session_state.step == "start":
    if st.button("Click to Start Experience"):
        st.session_state.step = "intro"
        st.rerun()

elif st.session_state.step == "intro":
    st.video("intro.mp4", autoplay=True)
    if st.button("Start Quiz"):
        st.session_state.step = "quiz"
        st.rerun()

elif st.session_state.step == "quiz":
    st.audio("bg_music.mp3", autoplay=True, loop=True)
    add_bg("wallpaper.jpg")
    st.title("EVS Quiz Challenge")
    
    # Quiz Logic: Tumhare column names ke saath
    for i, q in enumerate(st.session_state.questions):
        options = [q['optionA'], q['optionB'], q['optionC'], q['optionD']]
        random.shuffle(options)
        st.radio(f"Q{i+1}: {q['question']}", options, key=f"q{i}")
    
    if st.button("Submit Quiz"):
        st.session_state.step = "leaderboard"
        st.rerun()

elif st.session_state.step == "leaderboard":
    st.audio("bg_music.mp3", autoplay=True, loop=True)
    add_bg("wallpaper.jpg")
    st.title("🏆 Fancy Leaderboard")
    ld = pd.read_csv("leaderboard.csv")
    st.table(ld.sort_values(by='Score', ascending=False).style.format({"Score": "{:.0f}"}))
