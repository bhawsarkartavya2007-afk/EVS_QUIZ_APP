import streamlit as st
import pandas as pd
import random
import os
import base64

# --- PAGE CONFIG ---
st.set_page_config(page_title="EVS Quiz App", layout="wide")

# --- SIMPLE CSS (No crashing) ---
st.markdown("""
    <style>
    #MainMenu, header, footer {visibility: hidden !important;}
    .stApp {padding-top: 0px !important; margin-top: 0px !important;}
    video {width: 100% !important;}
    .stButton > button { padding: 15px 30px; background-color: white !important; color: black !important; border: 2px solid black !important; border-radius: 10px; }
    </style>
""", unsafe_html=True)

# --- SESSION STATE ---
if 'step' not in st.session_state:
    st.session_state.update(step='start_screen', current_q_index=0, score=0, name="", selected_qs=[])

# --- BACKGROUND HELPER ---
def add_bg(image_file):
    if os.path.exists(image_file):
        with open(image_file, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        st.markdown(f"""<style>.stApp {{ background: url(data:image/jpeg;base64,{encoded}); background-size: cover; }}</style>""", unsafe_html=True)

# --- APP FLOW ---
if st.session_state.step == 'start_screen':
    if st.button("Click to Experience"):
        st.session_state.step = 'intro'
        st.rerun()

elif st.session_state.step == 'intro':
    st.video("intro.mp4", autoplay=True)
    if st.button("Continue"):
        st.session_state.step = 'quiz'
        st.rerun()

elif st.session_state.step == 'quiz':
    add_bg("wallpaper.jpg")
    st.audio('bg_music.mp3', autoplay=True, loop=True)
    
    idx = st.session_state.current_q_index
    item = st.session_state.selected_qs[idx] if st.session_state.selected_qs else pd.read_excel("quiz_data.xlsx").sample(20).to_dict('records')[0]
    
    st.markdown(f"### Q{idx+1}: {item['question']}")
    options = [item['optionA'], item['optionB'], item['optionC'], item['optionD']]
    
    if f"answered_{idx}" not in st.session_state:
        for i, opt in enumerate(options):
            if st.button(opt, key=f"btn_{idx}_{i}"):
                st.session_state[f"answered_{idx}"] = opt
                if opt == item.get('correct answer'):
                    st.session_state.score += 1
                st.rerun()
    else:
        for opt in options:
            correct_ans = item.get('correct answer')
            chosen = st.session_state[f"answered_{idx}"]
            
            # Color Feedback
            if opt == correct_ans:
                st.button(f"✅ {opt}", key=f"f_{opt}", disabled=True, type="primary")
            elif opt == chosen and opt != correct_ans:
                st.button(f"❌ {opt}", key=f"f_{opt}", disabled=True, type="secondary")
            else:
                st.button(opt, key=f"f_{opt}", disabled=True)
        
        if st.button("Next Question ➡️"):
            st.session_state.current_q_index += 1
            st.rerun()

elif st.session_state.step == 'end':
    st.markdown(f"## Final Score: {st.session_state.score}")
