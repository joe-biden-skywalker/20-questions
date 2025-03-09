import streamlit as st
import json

# Attempt to read credentials
try:
    credentials_raw = st.secrets["GOOGLE_CREDENTIALS"]
    st.write("✅ Successfully loaded GOOGLE_CREDENTIALS from Streamlit secrets!")
    st.write("Raw Credentials:", credentials_raw)
except KeyError:
    st.error("❌ ERROR: Missing GOOGLE_CREDENTIALS in Streamlit secrets! Check your app settings.")
    st.stop()
except json.JSONDecodeError:
    st.error("⚠️ Could not parse GOOGLE_CREDENTIALS as JSON. Make sure it's correctly formatted in Streamlit secrets.")
    st.stop()
