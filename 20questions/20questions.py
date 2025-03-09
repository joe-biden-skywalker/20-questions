import streamlit as st
import json
from google.oauth2.service_account import Credentials
import gspread
import google.generativeai as genai
import pandas as pd

# Hardcoded GenAI API key
genai_api_key = "AIzaSyBV7OwC34Z4lFOQYSb26cM4-eR1Bb35HCY"

# Load Google Credentials from Streamlit secrets
try:
    credentials_raw = st.secrets["GOOGLE_CREDENTIALS"]  # This is already a string
    credentials_json = json.loads(credentials_raw)  # Convert string to a Python dictionary
    credentials_json["private_key"] = credentials_json["private_key"].replace("\\n", "\n")  # Fix newlines!
except KeyError:
    st.stop()
except json.JSONDecodeError:
    st.stop()

# Authenticate with Google Drive using the fixed JSON format
try:
    creds = Credentials.from_service_account_info(credentials_json, scopes=["https://www.googleapis.com/auth/drive"])
    client = gspread.authorize(creds)
except Exception as e:
    st.stop()

# Configure Google GenAI
genai.configure(api_key=genai_api_key)
model = genai.GenerativeModel("gemini-1.5-pro-latest")

# Load CSV file containing people for the game
@st.cache_data
def load_data():
    sheet = client.open("Enriched_Friend_Data").sheet1  # Adjust sheet name if needed
    data = sheet.get_all_records()
    return pd.DataFrame(data)

people_df = load_data()

# Initialize session state for the game
if "questions_asked" not in st.session_state:
    st.session_state.questions_asked = []
if "possible_people" not in st.session_state:
    st.session_state.possible_people = people_df.copy()
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "question_count" not in st.session_state:
    st.session_state.question_count = 0
if "game_started" not in st.session_state:
    st.session_state.game_started = False
if "current_question" not in st.session_state:
    st.session_state.current_question = ""

st.title("20 Questions Game")
st.write("I will guess who you are in 20 yes/no questions or less.")

# Function to generate a strategic yes/no question using GenAI
def generate_question():
    remaining_people = st.session_state.possible_people
    context = f"We are playing a 20 Questions game. You must guess a person based on yes/no answers. The remaining candidates have these descriptions: {remaining_people['Description'].tolist()}. Generate ONE strategic yes/no question to help narrow down the choices." 
    response = model.generate_content(context)
    return response.text.strip()

# Start game button
if not st.session_state.game_started:
    if st.button("Start Game"):
        st.session_state.game_started = True
        st.session_state.question_count = 0
        st.session_state.questions_asked = []
        st.session_state.possible_people = people_df.copy()
        st.session_state.current_question = generate_question()

# Game logic
if st.session_state.game_started and not st.session_state.game_over:
    if st.session_state.question_count < 20 and len(st.session_state.possible_people) > 1:
        st.write(f"**Question {st.session_state.question_count + 1}:** {st.session_state.current_question}")
        user_response = st.radio("Answer the question:", ["Yes", "No"], key=f"response_{st.session_state.question_count}")
        
        if st.button("Next Question"):
            st.session_state.questions_asked.append(st.session_state.current_question)
            st.session_state.question_count += 1
            
            # Filter possible people based on the response
            if user_response == "Yes":
                st.session_state.possible_people = st.session_state.possible_people.sample(frac=0.5)  # Temporary filtering logic
            else:
                st.session_state.possible_people = st.session_state.possible_people.sample(frac=0.5)  # Temporary filtering logic
            
            # Generate the next question
            if len(st.session_state.possible_people) > 1 and st.session_state.question_count < 20:
                st.session_state.current_question = generate_question()
            else:
                best_guess = st.session_state.possible_people.iloc[0]['Name'] if not st.session_state.possible_people.empty else "I couldn't guess!"
                st.write(f"I believe that you are {best_guess}!")
                st.session_state.game_over = True
    else:
        best_guess = st.session_state.possible_people.iloc[0]['Name'] if not st.session_state.possible_people.empty else "I couldn't guess!"
        st.write(f"I believe that you are {best_guess}!")
        st.session_state.game_over = True

# Reset game
if st.session_state.game_over and st.button("Play Again"):
    st.session_state.game_started = False
    st.session_state.game_over = False
    st.session_state.questions_asked = []
    st.session_state.possible_people = people_df.copy()
    st.session_state.question_count = 0
    st.session_state.current_question = ""
