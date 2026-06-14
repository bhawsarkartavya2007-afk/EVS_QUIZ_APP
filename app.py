import streamlit as st
import pandas as pd
import random
import time
import base64
import os

# --- Page Setup ---
st.set_page_config(page_title="EVS Quiz App", layout="wide")

# --- CSS Styling ---
st.markdown("""
    <style>
    #MainMenu, header, footer {visibility: hidden !important;}
    .stApp { padding-top: 0px !important; margin-top: 0px !important; }
    div[data-baseweb="input"] { background-color: white !important; }
    div[data-baseweb="input"] input { color: black !important; }
    
    /* Video aur Button Styling */
    video { width: 100% !important; height: auto !important; }
    .stButton > button {
        padding: 15px 30px; font-size: 18px; background-color: white !important; 
        color: black !important; border: 2px solid black !important;
        border-radius: 10px; font-weight: bold !important;
    }
    .block-container { padding: 2rem !important; background: rgba(255, 255, 255, 0.2); border-radius: 20px; border: 2px solid rgba(0,0,0,0.9) }
    audio { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# --- Background Image Function ---
def add_bg(image_file):
    if os.path.exists(image_file):
        with open(image_file, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        st.markdown(f"""<style>.stApp {{ background: url(data:image/jpeg;base64,{encoded}); background-size: cover; background-position: center; background-attachment: fixed; filter: saturate(1.5) brightness(0.9) }} p, div, label, h1, h2, h3 {{ color: black !important; font-weight: bold !important; }}</style>""", unsafe_allow_html=True)

# --- Helper Functions ---
@st.cache_data
def load_data():
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

# --- Initialize State ---
if 'step' not in st.session_state:
    st.session_state.update(step='start_screen', current_q_index=0, score=0, name="", selected_qs=[])

# --- Main Flow ---
if st.session_state.step == 'start_screen':
    if st.button("Click to Start Experience"):
        st.session_state.step = 'intro'
        st.rerun()

elif st.session_state.step == 'intro':
    st.video("intro.mp4", autoplay=True)
    time.sleep(10.4) 
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
    st.audio('bg_music.mp3', format='audio/mp3', autoplay=True, loop=True)
    
    idx = st.session_state.current_q_index
    item = st.session_state.selected_qs[idx]
    
    # State check: kya is question ka jawab diya ja chuka hai?
    if f"answered_{idx}" not in st.session_state:
        st.session_state[f"answered_{idx}"] = False
        
    if f"options_{idx}" not in st.session_state:
        opts = [item['optionA'], item['optionB'], item['optionC'], item['optionD']]
        random.shuffle(opts)
        st.session_state[f"options_{idx}"] = opts
        
    st.subheader(f"Q{idx+1}: {item['question']}")
    
    # Agar answer nahi diya, toh radio button dikhayein
    if not st.session_state[f"answered_{idx}"]:
        ans = st.radio("Choose the correct option:", st.session_state[f"options_{idx}"], key=f"q_{idx}")
        
        if st.button("Submit Answer"):
            st.session_state[f"answered_{idx}"] = True # Lock lag gaya
            
            # Answer ko normalize karein
            user_ans = str(ans).strip().lower()
            correct_ans = str(item['correct answer']).strip().lower()
            
            if user_ans == correct_ans:
                st.success("✅ Sahi Jawab!")
                st.session_state.score += 1
                st.session_state[f"last_ans_{idx}"] = ans
            else:
                st.error(f"❌ Galat Jawab! Sahi tha: {item['correct answer']}")
                st.session_state[f"last_ans_{idx}"] = ans
            st.rerun()
            
    # Agar answer diya ja chuka hai, toh feedback dikhayein aur "Next Question"
    else:
        # Feedback phir se dikhayein agar user refresh kare
        if st.session_state.get(f"last_ans_{idx}") == item['correct answer']:
            st.success("✅ Sahi Jawab!")
        else:
            st.error(f"❌ Galat Jawab! Sahi tha: {item['correct answer']}")
            
        if st.button("Next Question"):
            if idx < len(st.session_state.selected_qs) - 1:
                st.session_state.current_q_index += 1
                st.rerun()
            else:
                save_score(st.session_state.name, st.session_state.score)
                st.session_state.step = 'end'
                st.rerun()

elif st.session_state.step == 'end':
    add_bg("wallpaper.jpg")
    st.audio('bg_music.mp3', format='audio/mp3', autoplay=True, loop=True)
    st.success(f"Well done {st.session_state.name}!")
    st.subheader(f"Your Final Score: {st.session_state.score}/20")
    
    st.subheader("🏆 Leaderboard")
    # Leaderboard ke liye ek white background container banayein
    with st.container():
        st.markdown("""
            <style>
            div[data-testid="stTable"] {
                background-color: white !important;
                padding: 10px;
                border-radius: 10px;
            }
            div[data-testid="stTable"] td, div[data-testid="stTable"] th {
                color: black !important;
            }
            </style>
        """, unsafe_allow_html=True)
    if os.path.exists('leaderboard.csv'):
        df = pd.read_csv('leaderboard.csv')
        st.table(df.sort_values(by='Score', ascending=False).head(10))
        
    if st.button("Restart"):
        st.session_state.clear()
        st.rerun()
