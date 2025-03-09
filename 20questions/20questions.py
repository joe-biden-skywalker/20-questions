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
    st.error("❌ ERROR: Missing GOOGLE_CREDENTIALS in Streamlit secrets! Check your app settings.")
    st.stop()
except json.JSONDecodeError:
    st.error("⚠️ Could not parse GOOGLE_CREDENTIALS as JSON. Make sure it's correctly formatted in Streamlit secrets.")
    st.stop()

# Authenticate with Google Drive using the fixed JSON format
try:
    creds = Credentials.from_service_account_info(credentials_json, scopes=["https://www.googleapis.com/auth/drive"])
    client = gspread.authorize(creds)
except Exception as e:
    st.error(f"⚠️ Could not authenticate with Google Drive: {e}")
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

st.title("20 Questions Game")
st.write("Think of a person from the list, and I will try to guess who it is!")

# Generate a yes/no question to narrow down the possibilities
def generate_question():
    if st.session_state.possible_people.empty:
        return "I couldn't guess who you are thinking of! Try again."
    question_prompt = "Ask a yes or no question that will help identify a person from this list: " + ", ".join(people_df.columns)
    response = model.generate_content(question_prompt)
    return response.text.strip()

if st.button("Ask a Question"):
    question = generate_question()
    st.session_state.questions_asked.append(question)
    st.session_state.current_question = question
    st.write(f"**Question:** {question}")

# Handle user response
if "current_question" in st.session_state:
    user_response = st.radio("Answer the question:", ["Yes", "No"], key="user_response")
    if st.button("Submit Response"):
        # Filter people based on response (basic logic for now)
        if user_response == "Yes":
            st.session_state.possible_people = st.session_state.possible_people.sample(frac=0.5)  # Example filtering logic
        st.write(f"Remaining people: {len(st.session_state.possible_people)}")
        if len(st.session_state.possible_people) == 1:
            st.write(f"I guess you are thinking of: {st.session_state.possible_people.iloc[0]['Name']}")
            st.session_state.possible_people = people_df.copy()
            st.session_state.questions_asked = []
