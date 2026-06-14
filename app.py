import streamlit as st
import pandas as pd
import random
import time
import base64
import os

# Page Config
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# --- Pura CSS Block (Landscape, White Box, Audio/Video Control) ---
st.markdown("""
    <style>
    /* 1. Landscape Warning */
    @media only screen and (orientation: portrait) {
        .portrait-warning { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: white; z-index: 99999; display: flex; justify-content: center; align-items: center; font-size: 24px; font-weight: bold; color: black; text-align: center; padding: 20px; }
    }
    @media only screen and (orientation: landscape) { .portrait-warning { display: none; } }
    
    /* 2. Header/Footer aur White Patti hatana */
    #MainMenu, header, footer {visibility: hidden !important;}
    .stApp { padding-top: 0px !important; margin-top: -60px !important; }
     
    /* 3. Audio aur Video Controls hide karna */
    audio { display: none !important; }
    video::-webkit-media-controls { display: none !important; }
    
    /* 4. Name input aur Button ko White background aur Black font dena */
    .stTextInput > div > div > input {
        background-color: white !important;
        color: black !important;
        font-weight: bold !important;
    }
    .stButton > button {
        background-color: white !important;
        color: black !important;
        border: 2px solid black !important;
        font-weight: bold !important;
    }
    </style>
    <div class="portrait-warning">📱 Please rotate your device to LANDSCAPE mode!</div>
""", unsafe_allow_html=True)

# Audio Controller Function
if 'audio_file' not in st.session_state:
    st.session_state.audio_file = "intro_audio.mp3"
  
def play_audio():
    st.markdown(f'''
        <audio autoplay loop>
            <source src="{st.session_state.audio_file}" type="audio/mpeg">
        </audio>
    ''', unsafe_allow_html=True)
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
    # Audio-less video file ko load karo (jis mein music pehle se mix hai)
    with open("intro.mp4", "rb") as f:
        video_bytes = f.read()
    video_base64 = base64.b64encode(video_bytes).decode('utf-8')

    # Full screen CSS + Video tag (Audio ab video ke andar hai)
    st.markdown(f"""
        <style>
        .full-screen-video {{
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
            object-fit: cover; z-index: 9999;
        }}
        </style>
        <video class="full-screen-video" autoplay playsinline>
            <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
        </video>
    """, unsafe_allow_html=True)
    
    # st.audio wala code yahan se hata do, kyuki audio video mein hai
    
    time.sleep(13) # Video ki sahi lambai yahan likho
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
