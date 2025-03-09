import streamlit as st
import json
import gspread
from google.oauth2.service_account import Credentials

# Step 1: Load secrets correctly
try:
    credentials_json = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
    genai_api_key = st.secrets["GENAI_API_KEY"]
except KeyError as e:
    st.error(f"❌ ERROR: Missing {str(e)} in Streamlit secrets! Check your app settings.")
    st.stop()
except json.JSONDecodeError as e:
    st.error(f"❌ ERROR: Invalid JSON format in Google credentials: {e}")
    st.stop()

# Step 2: Debug - Check what keys exist in the credentials
st.write("Loaded keys:", list(credentials_json.keys()))  # TEMPORARY Debugging Line

# Step 3: Authenticate with Google Drive
try:
    creds = Credentials.from_service_account_info(credentials_json, scopes=["https://www.googleapis.com/auth/drive"])
    client = gspread.authorize(creds)
except Exception as e:
    st.error(f"⚠️ Could not authenticate with Google Drive: {e}")
    st.stop()
