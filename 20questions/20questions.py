import streamlit as st
import pandas as pd
import os
import json
from google.oauth2.service_account import Credentials
import gspread
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Authenticate with Google Drive API using environment variable
credentials_json = os.getenv("GOOGLE_CREDENTIALS")

if not credentials_json:
    st.error("❌ ERROR: Missing Google Drive credentials. Check your environment variables!")
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

st.title("🎭 20 Questions: Guess Your Friend!")

# Get list of attributes from CSV
if not df.empty:
    attribute_columns = [col for col in df.columns if col != "name"]
else:
    st.error("⚠️ No data found in the Google Drive file.")
    st.stop()

# Initialize session state for tracking progress
if "question_index" not in st.session_state:
    st.session_state.question_index = 0
    st.session_state.answers = {}
    st.session_state.remaining_friends = df.copy()

# Get the current question
if st.session_state.question_index < len(attribute_columns):
    attribute = attribute_columns[st.session_state.question_index]
    question_text = f"Do you {attribute.replace('_', ' ')}?"  # Format question

    st.write(question_text)

    col1, col2 = st.columns(2)
    if col1.button("Yes"):
        st.session_state.answers[attribute] = True
        st.session_state.question_index += 1
    if col2.button("No"):
        st.session_state.answers[attribute] = False
        st.session_state.question_index += 1

else:
    # Filter friend list based on answers
    for attribute, value in st.session_state.answers.items():
        st.session_state.remaining_friends = st.session_state.remaining_friends[
            st.session_state.remaining_friends[attribute] == value
        ]

    if len(st.session_state.remaining_friends) == 1:
        st.success(f"🎉 I think your friend is **{st.session_state.remaining_friends.iloc[0]['name']}**!")
    elif len(st.session_state.remaining_friends) > 1:
        st.info("🤔 I couldn't narrow it down to one person, but here are the possible matches:")
        for name in st.session_state.remaining_friends["name"]:
            st.write(f"- {name}")
    else:
        st.warning("😕 I couldn't find a match based on your answers!")

    if st.button("Restart"):
        st.session_state.question_index = 0
        st.session_state.answers = {}
        st.session_state.remaining_friends = df.copy()
