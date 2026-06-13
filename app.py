import streamlit as st
import pandas as pd
import random
import time
import base64
import os
st.markdown("""
    <head>
        <link rel="manifest" href="static/manifest.json">
    </head>
""", unsafe_allow_html=True)
# --- Page Configuration ---
st.set_page_config(page_title="EVS Quiz App", layout="wide")

# --- CSS for UI ---
st.markdown("""
    <style>
    #MainMenu, header, footer {visibility: hidden;}
    
    [data-testid="stVerticalBlock"] {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
    }
    
    .stButton > button {
        padding: 15px 30px;
        font-size: 18px;
        background-color: white !important; 
    color: black !important;             
    border: 2px solid black !important;  
    border-radius: 10px;
    font-weight: bold !important;
}

.stButton > button:hover {
    background-color: #f0f0f0 !important;
    color: black !important;
    border: 2px solid black !important;
    }
    
    .block-container {
        padding: 2rem !important; 
        background: rgba(255, 255, 255, 0.2); 
        border-radius: 20px;
        border: 2px solid rgba(0,0,0,0.9)
    }
    
    /* Audio bar hide karne ke liye */
    audio {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Background Image Function ---
def add_bg(image_file):
    if os.path.exists(image_file):
        with open(image_file, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background: url(data:image/jpeg;base64,{encoded});
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
                filter: saturate(1.5) brightness(0.9)
            }}
            p, div, label, h1, h2, h3, .stRadio label {{
                color: black !important;
                font-weight: bold !important;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_excel("quiz_data.xlsx")
    df.columns = df.columns.str.strip()
    return df.to_dict('records')

# --- Session Initialization ---
if 'step' not in st.session_state:
    st.session_state.update(step='start_screen', current_q_index=0, user_answers={}, score=0, name="", selected_qs=[])

# --- App Flow ---
if st.session_state.step == 'start_screen':
    if st.button("Click to Start Experience"):
        st.session_state.step = 'intro'
        st.rerun()

elif st.session_state.step == 'intro':
    st.video("intro.mp4", autoplay=True)
    time.sleep(10.3) 
    st.session_state.step = 'register'
    st.rerun()

elif st.session_state.step == 'register':
    add_bg("wallpaper.jpg")
    st.title("Registration")
    name = st.text_input("Enter your name:")
    if st.button("Start Quiz"):
        if name:
            st.session_state.name = name
            quiz_data = load_data()
            st.session_state.selected_qs = random.sample(quiz_data, min(20, len(quiz_data)))
            st.session_state.step = 'quiz'
            st.rerun()
        else:
            st.warning("Please enter your name!")

elif st.session_state.step == 'quiz':
    add_bg("wallpaper.jpg")
    # Audio loop mein aur hidden
    st.audio('bg_music.mp3', format='audio/mp3', autoplay=True, loop=True)
    
    idx = st.session_state.current_q_index
    item = st.session_state.selected_qs[idx]
    
    if f"options_{idx}" not in st.session_state:
        opts = [item['optionA'], item['optionB'], item['optionC'], item['optionD']]
        random.shuffle(opts)
        st.session_state[f"options_{idx}"] = opts
        
    st.subheader(f"Q{idx+1}: {item['question']}")
    ans = st.radio("Choose the correct option:", st.session_state[f"options_{idx}"], key=f"q_{idx}")
    
    if st.button("Next"):
        st.session_state.user_answers[idx] = ans
        if idx < len(st.session_state.selected_qs) - 1:
            st.session_state.current_q_index += 1
            st.rerun()
        else:
            st.session_state.score = sum(1 for i, q in enumerate(st.session_state.selected_qs) 
                                        if st.session_state.user_answers[i] == q['correct answer'])
            st.session_state.step = 'end'
            st.rerun()

elif st.session_state.step == 'end':
    add_bg("wallpaper.jpg")
    # Audio yahan bhi loop mein aur hidden
    st.audio('bg_music.mp3', format='audio/mp3', autoplay=True, loop=True)
    st.success(f"Well done {st.session_state.name}!")
    st.subheader(f"Your Final Score: {st.session_state.score}/20")
    
    score_data = pd.DataFrame({'Name': [st.session_state.name], 'Score': [st.session_state.score]})
    if os.path.exists('leaderboard.csv'):
        df_scores = pd.concat([pd.read_csv('leaderboard.csv'), score_data], ignore_index=True)
    else:
        df_scores = score_data
    df_scores.to_csv('leaderboard.csv', index=False)
    
    st.write("### 🏆 Leaderboard")
    st.table(df_scores.sort_values(by='Score', ascending=False).head(10))
    
    if st.button("Restart Quiz"):
        st.session_state.clear()
        st.rerun()
