Here's the complete corrected script with all necessary updates:

```python
import streamlit as st
from streamlit_oauth import OAuth2Component
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
import sys

# Add frontend assets path to system path (critical fix)
sys.path.append(str(Path(__file__).parent / "frontend/dist"))

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# --- Environment Variables Loading ---
st.write("## Debugging .env file path")
st.write(f"Current working directory: `{Path.cwd()}`")

# Verify .env file path
env_path = Path('.') / '.env'
st.write(f"Looking for .env at: `{env_path.resolve()}`")

if not env_path.exists():
    st.error(f".env file not found at: {env_path.absolute()}")
    st.stop()

load_dotenv(dotenv_path=env_path)

# --- Environment Variable Validation ---
def get_env_var(name):
    value = os.getenv(name)
    if not value:
        st.error(f"Missing required environment variable: {name}")
        st.stop()
    return value

# Clean Azure AD URLs (critical fix for Microsoft Entra ID)
AUTHORIZE_URL = get_env_var('AUTHORIZE_URL').replace("https://", "")
TOKEN_URL = get_env_var('TOKEN_URL').replace("https://", "")
CLIENT_ID = get_env_var('CLIENT_ID')
CLIENT_SECRET = get_env_var('CLIENT_SECRET')
REDIRECT_URI = get_env_var('REDIRECT_URI')
SCOPE = get_env_var('SCOPE')

# Optional endpoints
REFRESH_TOKEN_URL = os.getenv('REFRESH_TOKEN_URL', '').replace("https://", "") or None
REVOKE_TOKEN_URL = os.getenv('REVOKE_TOKEN_URL', '').replace("https://", "") or None

# Debug output
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
    authorize_endpoint=AUTHORIZE_URL,
    token_endpoint=TOKEN_URL,
    refresh_token_endpoint=REFRESH_TOKEN_URL,
    revoke_token_endpoint=REVOKE_TOKEN_URL,
    client_kwargs={
        "scope": SCOPE,
        "redirect_uri": REDIRECT_URI
    }
)

# --- Authentication Flow ---
if 'token' not in st.session_state:
    result = oauth2.authorize_button(
        name="Authorize with Microsoft",
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        key="azure_auth"
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
```

**Critical Requirements:**

1. **Package Installation:**
```bash
pip uninstall streamlit-oauth
pip install git+https://github.com/bfortuner/streamlit-oauth
```

2. **.env File Format (Microsoft Entra ID Example):**
```env
AUTHORIZE_URL=https://login.microsoftonline.com/YOUR_TENANT_ID/oauth2/v2.0/authorize
TOKEN_URL=https://login.microsoftonline.com/YOUR_TENANT_ID/oauth2/v2.0/token
CLIENT_ID=your_app_id
CLIENT_SECRET=your_app_secret
REDIRECT_URI=http://localhost:8501  # Must match Azure AD registration
SCOPE=openid email profile
```

**Key Fixes Implemented:**
1. Removed `https://` from Azure AD URLs to prevent path conversion errors
2. Added explicit frontend path resolution
3. Proper parameter naming for OAuth2Component
4. Added client_kwargs for scope and redirect_uri
5. Enhanced error handling for Microsoft Entra ID specific issues

**Verification Steps:**
1. Ensure your virtual environment contains the correct `streamlit-oauth` files
2. Confirm the frontend/dist directory exists in the package location
3. Verify all Azure AD endpoints match your app registration exactly
4. Check that the redirect URI is properly registered in Azure AD

This script should now handle Microsoft Entra ID authentication without the path conversion errors. The error you were seeing should be resolved through the combination of URL cleaning and proper package installation.
