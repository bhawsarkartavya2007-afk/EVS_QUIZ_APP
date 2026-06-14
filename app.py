import streamlit as st
import pandas as pd
import random
import os
import base64

# --- Page Setup ---
st.set_page_config(page_title="EVS Quiz App", layout="wide")

# --- UI Styling (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    .stButton > button { width: 100%; border-radius: 10px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- Initialize State ---
if 'step' not in st.session_state:
    st.session_state.update(
        step='home', 
        current_q_index=0, 
        score=0, 
        name="", 
        selected_qs=[]
    )

# --- Helper Functions ---
@st.cache_data
def load_data():
    # Aapki excel file ka path
    df = pd.read_excel("quiz_data.xlsx")
    df.columns = df.columns.str.strip()
    return df.to_dict('records')

def save_score(name, score):
    file = 'leaderboard.csv'
    data = {'Name': [name], 'Score': [score]}
    df_new = pd.DataFrame(data)
    if os.path.exists(file):
        df_old = pd.read_csv(file)
        df_final = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_final = df_new
    df_final.to_csv(file, index=False)

# --- App Pages ---

# 1. Home Page
if st.session_state.step == 'home':
    st.title("EVS Quiz App")
    name = st.text_input("Apna Naam Likhein:")
    if st.button("Start Quiz"):
        if name:
            st.session_state.name = name
            quiz_data = load_data()
            st.session_state.selected_qs = random.sample(quiz_data, min(20, len(quiz_data)))
            st.session_state.step = 'quiz'
            st.rerun()
        else:
            st.warning("Please apna naam enter karein!")

# 2. Quiz Page
elif st.session_state.step == 'quiz':
    idx = st.session_state.current_q_index
    item = st.session_state.selected_qs[idx]
    
    st.subheader(f"Q{idx+1}: {item['question']}")
    
    # Radio buttons for options
    options = [item['optionA'], item['optionB'], item['optionC'], item['optionD']]
    ans = st.radio("Choose the correct answer:", options, key=f"q_{idx}")
    
    if st.button("Next"):
        if ans == item['correct answer']:
            st.session_state.score += 1
            
        if idx < len(st.session_state.selected_qs) - 1:
            st.session_state.current_q_index += 1
            st.rerun()
        else:
            save_score(st.session_state.name, st.session_state.score)
            st.session_state.step = 'result'
            st.rerun()

# 3. Result Page
elif st.session_state.step == 'result':
    st.title("Quiz Complete! 🎉")
    st.write(f"Hello {st.session_state.name}, Your Score is: {st.session_state.score} / 20")
    
    st.subheader("Leaderboard")
    if os.path.exists('leaderboard.csv'):
        df = pd.read_csv('leaderboard.csv')
        # Sabse zyada score wale upar dikhenge
        df = df.sort_values(by='Score', ascending=False)
        st.table(df.head(10)) # Top 10 dikhayega
    
    if st.button("Play Again"):
        st.session_state.clear()
        st.rerun()
