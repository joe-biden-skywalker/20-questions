import streamlit as st
import json
import gspread
from google.oauth2.service_account import Credentials

# Load secrets from a single section
try:
    secrets = st.secrets["SECRETS"]  # Everything is under one key now
    credentials_json = json.loads(secrets["GOOGLE_CREDENTIALS"])
    genai_api_key = secrets["GENAI_API_KEY"]
except KeyError as e:
    st.error(f"❌ ERROR: Missing {str(e)} in Streamlit secrets! Check your app settings.")
    st.stop()
except json.JSONDecodeError as e:
    st.error(f"❌ ERROR: Invalid JSON format in Google credentials: {e}")
    st.stop()

# Debugging: Ensure private_key exists and is correctly formatted
if "private_key" not in credentials_json:
    st.error("❌ ERROR: Missing 'private_key' in Google credentials!")
    st.stop()

# Ensure private key is formatted correctly
credentials_json["private_key"] = credentials_json["private_key"].replace("\\n", "\n")

# Authenticate with Google Drive
try:
    creds = Credentials.from_service_account_info(credentials_json, scopes=["https://www.googleapis.com/auth/drive"])
    client = gspread.authorize(creds)
    st.success("✅ Successfully authenticated with Google Drive!")
except Exception as e:
    st.error(f"⚠️ Could not authenticate with Google Drive: {e}")
    st.stop()
