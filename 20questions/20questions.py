import streamlit as st
import pandas as pd
import os
import json
from google.oauth2.service_account import Credentials
import gspread
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Authenticate with Google Drive API using environment variable
credentials_json = os.getenv("GOOGLE_CREDENTIALS")

genai_api_key = os.getenv("GENAI_API_KEY")  # Google GenAI API Key

if not credentials_json:
    st.error("❌ ERROR: Missing Google Drive credentials. Check your environment variables!")
    st.stop()

if not genai_api_key:
    st.error("❌ ERROR: Missing Google GenAI API Key. Check your environment variables!")
    st.stop()

creds_dict = json.loads(credentials_json)
creds = Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/drive"])
client = gspread.authorize(creds)

# Google Drive file details
spreadsheet_name = "Enriched_Friend_Data"  # Update if needed

try:
    # Open the spreadsheet and fetch data
    sheet = client.open(spreadsheet_name).sheet1
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
except Exception as e:
    st.error(f"⚠️ Could not fetch data from Google Drive: {e}")
    st.stop()

# Debugging: Display column names and first few rows
st.write("Column Names:", df.columns.tolist())
st.write("First Few Rows:", df.head())

# Ensure that the dataframe is not empty
if df.empty:
    st.error("❌ ERROR: The data appears to be empty. Please check the source file.")
    st.stop()

# Configure Google GenAI
model = genai.GenerativeModel("gemini-pro")

def generate_smart_question(description, previous_questions=[]):
    """
    Uses Google GenAI to generate a more natural and intelligent question
    based on the description field.
    """
    prompt = f"Based on the following description: '{description}', generate a yes/no question to help narrow down possible matches. Avoid repeating these questions: {previous_questions}."
    response = model.generate_content(prompt)
    return response.text if response else "Do you know this person?"

st.title("20 Questions AI-Powered Friend Guessing Game")

# Initialize game state
if "questions_asked" not in st.session_state:
    st.session_state["questions_asked"] = []
    st.session_state["remaining_friends"] = df.copy()
    st.session_state["answers"] = {}

def ask_next_question():
    """Ask the next question based on remaining friend descriptions."""
    if st.session_state["remaining_friends"].empty:
        st.write("No more friends left to guess!")
        return None
    
    friend_sample = st.session_state["remaining_friends"].sample(1).iloc[0]
    question = generate_smart_question(friend_sample.get("Description", ""), st.session_state["questions_asked"])
    st.session_state["questions_asked"].append(question)
    return question, friend_sample.get("Name", "Unknown")

def narrow_down_choices(answer, friend_name):
    """Eliminate friends based on the yes/no responses."""
    if answer == "Yes":
        st.session_state["remaining_friends"] = st.session_state["remaining_friends"][st.session_state["remaining_friends"].get("Name") == friend_name]
    else:
        st.session_state["remaining_friends"] = st.session_state["remaining_friends"][st.session_state["remaining_friends"].get("Name") != friend_name]

# Display the question and get user input
if st.button("Ask a Question"):
    question_data = ask_next_question()
    if question_data:
        question, friend_name = question_data
        st.write(question)
        yes_no = st.radio("Answer:", ["Yes", "No"], key=question)
        if st.button("Submit Answer"):
            narrow_down_choices(yes_no, friend_name)
            if len(st.session_state["remaining_friends"]) == 1:
                st.success(f"I think your friend is {st.session_state['remaining_friends'].iloc[0]['Name']}!")
