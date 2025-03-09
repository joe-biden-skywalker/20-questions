import streamlit as st
import pandas as pd
import json
import ast
from google.oauth2.service_account import Credentials
import gspread
import google.generativeai as genai

# Hardcoded GenAI API key
genai_api_key = "AIzaSyBV7OwC34Z4lFOQYSb26cM4-eR1Bb35HCY"

# Authenticate with Google Drive API using Streamlit secrets
try:
    credentials_json = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
except KeyError as e:
    st.error(f"❌ ERROR: Missing {str(e)} in Streamlit secrets! Check your app settings.")
    st.stop()
except Exception as e:
    st.error(f"⚠️ Could not load secrets: {e}")
    st.stop()

try:
    creds = Credentials.from_service_account_info(credentials_json, scopes=["https://www.googleapis.com/auth/drive"])
    client = gspread.authorize(creds)
    st.success("✅ Successfully authenticated with Google Drive!")
except Exception as e:
    st.error(f"⚠️ Could not authenticate with Google Drive: {e}")
    st.stop()

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

# Ensure that the dataframe is not empty
if df.empty:
    st.error("❌ ERROR: The data appears to be empty. Please check the source file.")
    st.stop()

# Configure Google GenAI
genai.configure(api_key=genai_api_key)
model = genai.GenerativeModel("gemini-pro")

def generate_smart_question(remaining_friends, previous_questions=[]):
    """
    Uses Google GenAI to generate a strategic yes/no question to eliminate the most possible friends.
    """
    if remaining_friends.empty:
        return "Are you thinking of someone?"
    
    prompt = (
        "You are playing 20 Questions. Based on the following list of friend descriptions, "
        "generate a yes/no question that will help narrow down who the player is thinking of: "
        f"{remaining_friends['Description'].tolist()}. Avoid repeating these questions: {previous_questions}."
    )
    response = model.generate_content(prompt)
    return response.text.strip() if response else "Do you know this person?"

st.title("20 Questions AI-Powered Friend Guessing Game")

# Initialize game state
if "questions_asked" not in st.session_state:
    st.session_state["questions_asked"] = []
    st.session_state["remaining_friends"] = df.copy()
    st.session_state["question_history"] = []
    st.session_state["current_question"] = ""

# Generate and ask a question if there are still multiple options
if len(st.session_state["remaining_friends"]) > 1:
    if not st.session_state["current_question"]:
        st.session_state["current_question"] = generate_smart_question(
            st.session_state["remaining_friends"], st.session_state["question_history"]
        )
    
    st.write(st.session_state["current_question"])
    yes_no = st.radio("Your Answer:", ["Yes", "No"], key="answer")
    
    if st.button("Submit Answer"):
        st.session_state["question_history"].append(st.session_state["current_question"])
        
        # Narrow down choices based on response
        if yes_no == "Yes":
            st.session_state["remaining_friends"] = st.session_state["remaining_friends"][
                st.session_state["remaining_friends"]["Description"].str.contains(st.session_state["current_question"], case=False, na=False)
            ]
        else:
            st.session_state["remaining_friends"] = st.session_state["remaining_friends"][
                ~st.session_state["remaining_friends"]["Description"].str.contains(st.session_state["current_question"], case=False, na=False)
            ]
        
        # Reset question
        st.session_state["current_question"] = ""
        st.rerun()
        
# If only one friend remains, make the final guess
if len(st.session_state["remaining_friends"]) == 1:
    st.success(f"I think your friend is {st.session_state['remaining_friends'].iloc[0]['Name']}!")
