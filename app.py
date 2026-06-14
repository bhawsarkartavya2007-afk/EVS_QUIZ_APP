import streamlit as st
import pandas as pd
import random
import os
import base64
st.set_page_config(page_title="EVS Quiz App", layout="wide"
st.markdown("""
    <style>
    #MainMenu, header, footer {visibility: hidden !important;}
    .stApp {padding-top: 0px !important; margin-top: 0px !important;}
    audio {display: none !important;}
    p, div, label, h1, h2, h3 { color: black !important; font-weight: bold !important; }
    .stButton > button { padding: 15px 30px; background-color: white !important; color: black !important; border: 2px solid black !important; border-radius: 10px; font-weight: bold !important;}
    </style>
""", unsafe_html=True)
                   
def add_bg(image_file):
    if os.path.exists(image_file):
        with open(image_file, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        st.markdown(f"""<style>.stApp {{ background: url(data:image/jpeg;base64,{encoded}); background-size: cover; background-attachment: fixed; }}</style>""", unsafe_html=True)

# --- SESSION STATE ---
if 'step' not in st.session_state:
    st.session_state.update(step='start_screen', current_q_index=0, score=0, name="", selected_qs=[], show_page=None)

# --- APP FLOW ---
if st.session_state.step == 'start_screen':
    if st.button("Click to Experience"):
        st.session_state.step = 'intro'
        st.rerun()

elif st.session_state.step == 'intro':
    st.video("intro.mp4", autoplay=True)
    time.sleep(10)
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
            is_correct = (opt == item.get('correct answer'))
            is_chosen = (opt == st.session_state.get(f"choice_{idx}"))
            btn_type = "primary" if is_correct else ("secondary" if is_chosen else "secondary")
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
    st.markdown(f"## Well done {st.session_state.name}!")
    st.markdown(f"### Your Final Score: {st.session_state.score}/20")
    
    st.write("--- LEADERBOARD ---")
    if os.path.exists('leaderboard.csv'):
        df = pd.read_csv('leaderboard.csv')
        st.table(df.sort_values(by='Score', ascending=False).head(10))
    
    if st.button("Restart Quiz"):
        st.session_state.clear()
        st.rerun()
