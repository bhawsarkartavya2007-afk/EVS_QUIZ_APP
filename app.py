import streamlit as st
import pandas as pd
import random
import time
import base64
import os
# 1. CSS (Ise top par rehne do)
st.markdown("""
    <style>
    #MainMenu, header, footer { visibility: hidden !important; }
    .stApp { padding-top: 0px !important; margin-top: 0px !important; }
    </style>
""", unsafe_allow_html=True)

# 2. Session state setup
if 'question_index' not in st.session_state:
    st.session_state.question_index = 0
    st.session_state.score = 0
    st.session_state.quiz_finished = False

# 3. Quiz ka Logic
if not st.session_state.quiz_finished:
    # Yahan apne questions ki list banao
    questions = [
        {"q": "Q1: Swachh Bharat Abhiyan kab shuru hua?", "options": ["2014", "2015", "2016"], "ans": "2014"},
        # ... apne baaki questions yahan add karo ...
    ]
    
    if st.session_state.question_index < len(questions):
        q_data = questions[st.session_state.question_index]
        st.write(q_data["q"])
        user_choice = st.radio("Options:", q_data["options"], key="radio")
        
        if st.button("Submit"):
            if user_choice == q_data["ans"]:
                st.success("✅ Sahi Jawab!")
                st.session_state.score += 1
            else:
                st.error(f"❌ Galat! Sahi jawab: {q_data['ans']}")
            
            time.sleep(2) # 2 sec ruk kar next question
            st.session_state.question_index += 1
            st.rerun()
    else:
        st.session_state.quiz_finished = True
        st.rerun()

# 4. Quiz Khatam hone par
else:
    st.write(f"Quiz khatam! Tumhare points: {st.session_state.score}")
    if st.button("🏆 Leaderboard"):
        st.write("Leaderboard dikha raha hoon...")
    if st.button("🔄 Restart"):
        st.session_state.clear()
        st.rerun()
st.markdown("""
    <style>
    /* 1. Header, menu, footer hide karo */
    #MainMenu, header, footer {
        visibility: hidden !important;
    }

    /* 2. Mobile ki top white strip ko hata kar app ko full screen karne ke liye */
    .stApp {
        padding-top: 0px !important;
        margin-top: 0px !important;
    }

    /* 3. Landscape mode force karne ka logic */
    @media screen and (orientation: portrait) {
        body {
            transform: rotate(90deg);
            transform-origin: left top;
            width: 100vh;
            height: 100vw;
            overflow-x: hidden;
            position: absolute;
            top: 0;
            left: 0;
        }
    }

    /* 4. Input field styling (jo file 2735b2f9-aed5-4ed8-8c2c-f198a0b5344f mein hai) */
    div[data-baseweb="input"] {
        background-color: white !important;
    }
    div[data-baseweb="input"] input {
        color: black !important;
    }
    </style>
""", unsafe_allow_html=True)
if 'user_responses' not in st.session_state:
    st.session_state.user_responses = []
st.markdown("""
    <head>
        <link rel="manifest" href="static/site.webmanifest">
        <script>
            if ('serviceWorker' in navigator) {
                navigator.serviceWorker.register('static/service-worker.js')
                .then(() => console.log('Service Worker registered!'));
            }
        </script>
    </head>
""", unsafe_allow_html=True)
# --- Page Configuration ---
st.set_page_config(
    page_title="EVS Quiz App",
    page_icon="static/logo.png",
 layout="wide"
)

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
    with st.expander("Watch Intro Video", expanded=True):
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
        st.session_state.user_responses.append({
            "question": item['question'],
            "user_choice": ans,
            "correct_answer": item['correct answer']  # Ye tumhari Excel/Data mein jo column sahi answer ka hai, wahi likhna
        })
        if idx < len(st.session_state.selected_qs) - 1:
            st.session_state.current_q_index += 1
            st.rerun()
        else:
            st.session_state.score = sum(1 for i, q in enumerate(st.session_state.selected_qs) 
                                        if st.session_state.user_answers[i] == q['correct answer'])
            st.session_state.step = 'end'
            st.rerun()

elif st.session_state.step == 'end':
        st.markdown("""
    <style>
    /* Expander aur container ke background ko force karo */
    [data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border: none !important;
    }
    
    /* Expander ke andar ke element ka background */
    [data-testid="stExpander"] div[role="button"] {
        background-color: #FFFFFF !important;
    }
    
    /* Agar tum st.container ya st.verticalBlock use kar rahe ho */
    div[data-testid="stVerticalBlock"] {
        background-color: #FFFFFF !important;
        padding: 20px !important;
        border-radius: 10px !important;
    }
    
    /* Text color fix */
    div, p, label, h1, h2, h3 {
        color: #000000 !important;
    }
    </style>
""", unsafe_allow_html=True)
        
        add_bg("wallpaper.jpg")
        st.audio('bg_music.mp3', format='audio/mp3', autoplay=True, loop=True)
        st.success(f"Well done {st.session_state.name}!")
        st.subheader(f"Your Final Score: {st.session_state.score}/20")

        # 1. Buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("View Detailed Results"):
                st.session_state.show_page = "results"
        with col2:
            if st.button("View Leaderboard"):
                st.session_state.show_page = "leaderboard"

        # 2. Results Logic
        if st.session_state.get("show_page") == "results":
            with st.expander("Click to see your detailed results", expanded=True):
                for i, item in enumerate(st.session_state.user_responses):
                    st.write(f"**Question {i+1}:** {item['question']}")
                    st.write(f"Your choice: {item['user_choice']}")
                    
                    # 'correct_answer' key check karke error hatao
                    correct = item.get('correct_answer')
                    if item['user_choice'] == correct:
                        st.success("Correct!")
                    else:
                        st.error(f"Incorrect. The correct answer was: {correct}")
                    st.divider()
                    
# --- 1. QUIZ KA CODE (Jab tak quiz khatam nahi hota) ---
if not st.session_state.get("quiz_finished", False):
    # Yahan tumhare 20 questions waala sara code aayega
    # Jab 20th question submit ho jaye, toh bas ye likhna:
    # st.session_state.quiz_finished = True
    # st.rerun()
    st.write("Quiz chal raha hai...") 

# --- 2. RESULT KA CODE (Sirf quiz khatam hone ke baad) ---
else:
    st.subheader("Quiz Completed! 🎉")
    
    # Buttons ka menu
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📝 Details"):
            st.session_state.show_page = "results"
            st.rerun()
    with col2:
        if st.button("🔄 Restart"):
            st.session_state.clear()
            st.rerun()
    with col3:
        if st.button("🏆 Leaderboard"):
            st.session_state.show_page = "leaderboard"
            st.rerun()

    # Page navigation logic
    if st.session_state.get("show_page") == "results":
        st.subheader("📝 Detailed Results")
        with st.expander("Click to see your detailed results", expanded=True):
            for i, item in enumerate(st.session_state.user_responses):
                st.write(f"**Q{i+1}:** {item['question']}")
                st.write(f"Your choice: {item['user_choice']}")
                if item['user_choice'] == item.get('correct_answer'):
                    st.success("✅ Correct!")
                else:
                    st.error(f"❌ Incorrect. Correct was: {item.get('correct_answer')}")
                st.divider()
        if st.button("⬅️ Back to Menu"):
            st.session_state.show_page = None
            st.rerun()

    elif st.session_state.get("show_page") == "leaderboard":
        st.subheader("🏆 Leaderboard")
        if os.path.exists('leaderboard.csv'):
            df = pd.read_csv('leaderboard.csv')
            df = df.sort_values(by='Score', ascending=False).head(100)
            st.table(df)
        if st.button("⬅️ Back to Menu"):
            st.session_state.show_page = None
            st.rerun()
