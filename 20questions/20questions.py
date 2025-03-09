import streamlit as st
import json
from google.oauth2.service_account import Credentials
import gspread

# Load Google Credentials from Streamlit secrets
try:
    credentials_raw = st.secrets["GOOGLE_CREDENTIALS"]  # This is already a string
    credentials_json = json.loads(credentials_raw)  # Convert string to a Python dictionary
    st.write("✅ Successfully loaded GOOGLE_CREDENTIALS from Streamlit secrets!")  # Debugging
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
    st.success("✅ Successfully authenticated with Google Drive!")
except Exception as e:
    st.error(f"⚠️ Could not authenticate with Google Drive: {e}")
    st.stop()
