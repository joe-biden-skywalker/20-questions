import streamlit as st
import json
from google.oauth2.service_account import Credentials
import gspread
import google.generativeai as genai

# Hardcoded GenAI API key
genai_api_key = "AIzaSyBV7OwC34Z4lFOQYSb26cM4-eR1Bb35HCY"

# Load Google Credentials from Streamlit secrets
try:
    credentials_raw = st.secrets["GOOGLE_CREDENTIALS"]  # This is already a string
    credentials_json = json.loads(credentials_raw)  # Convert string to a Python dictionary
    credentials_json["private_key"] = credentials_json["private_key"].replace("\\n", "\n")  # Fix newlines!
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

# Configure Google GenAI
genai.configure(api_key=genai_api_key)
model = genai.GenerativeModel("gemini-pro")

# Test question to GenAI
response = model.generate_content("What is the capital of France?")
st.write("Test Response:", response.text)
