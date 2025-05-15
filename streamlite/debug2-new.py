import streamlit as st
from streamlit_oauth import OAuth2Component
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# --- Environment Variables Loading ---
# Verify .env file path
env_path = Path('.') / '.env'
if not env_path.exists():
    st.error(f".env file not found at: {env_path.absolute()}")
    st.stop()

# Load environment variables
load_dotenv(dotenv_path=env_path)

# Get environment variables with validation
def get_env_var(name):
    value = os.getenv(name)
    if not value:
        st.error(f"Missing required environment variable: {name}")
        st.stop()
    return value

AUTHORIZE_URL = get_env_var('AUTHORIZE_URL')
TOKEN_URL = get_env_var('TOKEN_URL')
REFRESH_TOKEN_URL = get_env_var('REFRESH_TOKEN_URL') if os.getenv('REFRESH_TOKEN_URL') else None
REVOKE_TOKEN_URL = get_env_var('REVOKE_TOKEN_URL') if os.getenv('REVOKE_TOKEN_URL') else None
CLIENT_ID = get_env_var('CLIENT_ID')
CLIENT_SECRET = get_env_var('CLIENT_SECRET')
REDIRECT_URI = get_env_var('REDIRECT_URI')
SCOPE = get_env_var('SCOPE')

# Debug print environment variables (remove in production)
st.write("Loaded environment variables:")
st.json({
    "AUTHORIZE_URL": AUTHORIZE_URL,
    "TOKEN_URL": TOKEN_URL,
    "CLIENT_ID": CLIENT_ID,
    "REDIRECT_URI": REDIRECT_URI,
    "SCOPE": SCOPE
})

# --- OAuth Configuration ---
oauth2 = OAuth2Component(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    authorize_url=AUTHORIZE_URL,
    token_url=TOKEN_URL,
    refresh_token_url=REFRESH_TOKEN_URL,
    revoke_token_url=REVOKE_TOKEN_URL
)

# --- Authentication Flow ---
if 'token' not in st.session_state:
    result = oauth2.authorize_button(
        name="Authorize",
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        key="authorize"
    )
    
    if result and 'token' in result:
        st.session_state.token = result['token']
        st.rerun()
else:
    token = st.session_state.token
    st.subheader("Current Token:")
    st.json(token)
    
    if st.button("Refresh Token"):
        try:
            new_token = oauth2.refresh_token(token)
            st.session_state.token = new_token
            st.rerun()
        except Exception as e:
            st.error(f"Token refresh failed: {str(e)}")

# Verify .env file path
from pathlib import Path

# Debug current working directory
st.write("## Debugging .env file path")
st.write(f"Current working directory: `{Path.cwd()}`")

env_path = Path('.') / '.env'
st.write(f"Looking for .env at: `{env_path.resolve()}`")

if not env_path.exists():
    st.error(f".env file not found at: `{env_path.absolute()`}")
    st.write("Directory contents:")
    for f in Path('.').iterdir():
        st.write(f"- `{f}`")
    st.stop()
else:
    st.success(f"Found .env file at: `{env_path.resolve()}`")
