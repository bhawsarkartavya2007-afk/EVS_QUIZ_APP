import streamlit as st
import pandas as pd
import random
import time
import base64
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="EVS Quiz App", layout="wide", initial_sidebar_state="collapsed")

# --- CSS & JAVASCRIPT ---
st.markdown("""
    <style>
    /* Mobile/Desktop UI Clean Up */
    #MainMenu, header, footer {visibility: hidden !important;}
    .stApp {padding-top: 0px !important; margin-top: 0px !important;}
    
    /* Hide Video/Audio Controls */
    video::-webkit-media-controls {display: none !important;}
    audio {display: none !important;}
    
    /* Text Styling */
    p, div, label, h1, h2, h3 { color: black !important; font-weight: bold !important; }
    .stButton > button { padding: 10px 20px; background-color: white !important; color: black !important; border: 2px solid black !important; border-radius: 10px; font-weight: bold !important;}
    </style>
    
    <script>
    function triggerFullScreen() {
        var elem = document.documentElement;
        if (elem.requestFullscreen) { elem.requestFullscreen(); }
        else if (elem.webkitRequestFullscreen) { elem.webkitRequestFullscreen(); }
    }
    </script>
""", unsafe_html=True)

# --- SESSION STATE ---
if 'step' not in st.session_state:
    st.session_state.update(step='start_screen', current_q_index=0, score=0, name="", selected_qs=[], show_page=None)

# --- HELPER FUNCTIONS ---
def add_bg(image_file):
    if os.path.exists(image_file):
        with open(image_file, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        st.markdown(f"""<style>.stApp {{ background: url(data:image/jpeg;base64,{encoded}); background-size: cover; background-attachment: fixed; }}</style>""", unsafe_html=True)

# --- APP FLOW ---
if st.session_state.step == 'start_screen':
    # Button click par full screen trigger hoga
    if st.button("Click to Experience", on_click=lambda: st.write('<script>triggerFullScreen();</script>', unsafe_allow_html=True)):
        st.session_state.step = 'intro'
        st.rerun()

elif st.session_state.step == 'intro':
    st.video("intro.mp4", autoplay=True)
    time.sleep(10) # Intro duration
    st.session_state.step = 'register'
    st.rerun()

elif st.session_state.step == 'register':
    add_bg("wallpaper.jpg")
    name = st.text_input("Enter your name:")
    if st.button("Start Quiz"):
        if name:
            st.session_state.name = name
            df = pd.read_excel("quiz_data.xlsx")
            st.session_state.selected_qs = df.sample(20).to_dict('records')
            st.session_state.step = 'quiz'
            st.rerun()

elif st.session_state.step == 'quiz':
    add_bg("wallpaper.jpg")
    st.audio('bg_music.mp3', autoplay=True, loop=True)
    
    idx = st.session_state.current_q_index
    item = st.session_state.selected_qs[idx]
    
    st.markdown(f"### Q{idx+1}: {item['question']}")
    
    if f"opts_{idx}" not in st.session_state:
        opts = [item['optionA'], item['optionB'], item['optionC'], item['optionD']]
        random.shuffle(opts)
        st.session_state[f"opts_{idx}"] = opts
        st.session_state[f"clicked_{idx}"] = False

    for opt in st.session_state[f"opts_{idx}"]:
        btn_key = f"btn_{idx}_{opt}"
        if not st.session_state[f"clicked_{idx}"]:
            if st.button(opt, key=btn_key):
                st.session_state[f"clicked_{idx}"] = True
                st.session_state[f"choice_{idx}"] = opt
                if opt == item.get('correct answer'):
                    st.session_state.score += 1
                st.rerun()
        else:
            # Color Feedback Logic
            btn_type = "primary" if opt == item.get('correct answer') else "secondary"
            st.button(opt, key=btn_key, type=btn_type, disabled=True)

    if st.session_state.get(f"clicked_{idx}"):
        if st.button("Next Question ➡️"):
            if idx < 19:
                st.session_state.current_q_index += 1
                st.rerun()
            else:
                st.session_state.step = 'end'
                st.rerun()

elif st.session_state.step == 'end':
    add_bg("wallpaper.jpg")
    st.markdown(f"## Final Score: {st.session_state.score}/20")
    if st.button("🏆 View Leaderboard"):
        st.session_state.show_page = "leaderboard"
        st.rerun()
        
    if st.session_state.show_page == "leaderboard":
        if os.path.exists('leaderboard.csv'):
            st.table(pd.read_csv('leaderboard.csv').sort_values(by='Score', ascending=False))
