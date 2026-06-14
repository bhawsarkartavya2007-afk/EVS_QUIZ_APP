import streamlit as st
import pandas as pd
import random
import time
import base64
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="EVS Quiz App", layout="wide")
st.markdown("""<style>#MainMenu, header, footer {visibility: hidden;} .stApp {padding-top: 0px;}</style>""", unsafe_allow_html=True)

# --- SESSION STATE ---
if 'step' not in st.session_state:
    st.session_state.update(step='start_screen', current_q_index=0, score=0, name="", selected_qs=[], show_page=None)

# --- HELPER FUNCTIONS ---
def add_bg(image_file):
    if os.path.exists(image_file):
        with open(image_file, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        st.markdown(f"""<style>.stApp {{ background: url(data:image/jpeg;base64,{encoded}); background-size: cover; }}</style>""", unsafe_allow_html=True)

def load_data():
    df = pd.read_excel("quiz_data.xlsx")
    df.columns = df.columns.str.strip()
    return df.to_dict('records')

# --- APP FLOW ---
if st.session_state.step == 'start_screen':
    if st.button("Click to Start Experience"):
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
            st.session_state.selected_qs = random.sample(load_data(), 20)
            st.session_state.step = 'quiz'
            st.rerun()

elif st.session_state.step == 'quiz':
    add_bg("wallpaper.jpg")
    idx = st.session_state.current_q_index
    item = st.session_state.selected_qs[idx]
    
    st.subheader(f"Q{idx+1}: {item['question']}")
    
    if f"opts_{idx}" not in st.session_state:
        opts = [item['optionA'], item['optionB'], item['optionC'], item['optionD']]
        random.shuffle(opts)
        st.session_state[f"opts_{idx}"] = opts
        st.session_state[f"clicked_{idx}"] = False
        st.session_state[f"choice_{idx}"] = None

    for opt in st.session_state[f"opts_{idx}"]:
        if not st.session_state[f"clicked_{idx}"]:
            if st.button(opt, key=opt):
                st.session_state[f"clicked_{idx}"] = True
                st.session_state[f"choice_{idx}"] = opt
                if opt == item['correct answer']:
                    st.session_state.score += 1
                st.rerun()
        else:
            # Color Feedback Logic
            btn_type = "primary" if opt == item['correct answer'] else ("secondary" if opt == st.session_state[f"choice_{idx}"] else "secondary")
            st.button(opt, key=opt, type=btn_type, disabled=True)

    if st.session_state[f"clicked_{idx}"]:
        if st.button("Next Question ➡️"):
            if idx < 19:
                st.session_state.current_q_index += 1
                st.rerun()
            else:
                st.session_state.step = 'end'
                st.rerun()

elif st.session_state.step == 'end':
    add_bg("wallpaper.jpg")
    st.subheader(f"Well done {st.session_state.name}!")
    st.write(f"## Final Score: {st.session_state.score}/20")
    
    if st.button("🏆 View Leaderboard"):
        st.session_state.show_page = "leaderboard"
        
    if st.session_state.show_page == "leaderboard":
        # Yahan apni CSV load karo
        st.write("--- LEADERBOARD ---")
        if os.path.exists('leaderboard.csv'):
            st.table(pd.read_csv('leaderboard.csv').sort_values(by='Score', ascending=False))
        if st.button("Restart"):
            st.session_state.clear()
            st.rerun()
