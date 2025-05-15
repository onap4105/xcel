This error occurs because the `streamlit-oauth` package is trying to resolve your OAuth endpoint URLs as local file paths. Let's fix this with a workaround:

### Updated Script with Critical Fixes:
```python
import streamlit as st
from streamlit_oauth import OAuth2Component
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
import sys
from urllib.parse import urlparse

# Critical fix: Add component directory to path
sys.path.append(str(Path(__file__).parent / "frontend/dist"))

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# --- Environment Variables Loading ---
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# --- Custom Component Handler Fix ---
from streamlit.web.server import Server
from tornado.web import RequestHandler

class FixedComponentRequestHandler(RequestHandler):
    def get(self, path: str = "") -> None:
        # Bypass URL path conversion
        if 'x3a' in path:  # Skip conversion for URL paths
            self.set_status(404)
            return
            
        # Original logic for component files
        abspath = os.path.abspath(
            os.path.join(
                os.path.join(Server.get_current().static_file_prefix, "components"),
                path,
            )
        )
        self.render(abspath)

# Monkey-patch the handler
Server._handlers[0][1][-1] = (r"/component/(.*)", FixedComponentRequestHandler, {})

# --- Environment Variables ---
def get_env_var(name):
    value = os.getenv(name)
    if not value:
        st.error(f"Missing required environment variable: {name}")
        st.stop()
    return value

# Modified URLs to prevent path conversion
AUTHORIZE_URL = get_env_var('AUTHORIZE_URL').replace("https://", "oauth/")
TOKEN_URL = get_env_var('TOKEN_URL').replace("https://", "oauth/")
CLIENT_ID = get_env_var('CLIENT_ID')
CLIENT_SECRET = get_env_var('CLIENT_SECRET')
REDIRECT_URI = get_env_var('REDIRECT_URI')
SCOPE = get_env_var('SCOPE')

# --- OAuth Configuration ---
oauth2 = OAuth2Component(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    authorize_url=AUTHORIZE_URL,
    token_url=TOKEN_URL,
    client_kwargs={
        "scope": SCOPE,
        "redirect_uri": REDIRECT_URI
    }
)

# --- Authentication Flow ---
if 'token' not in st.session_state:
    result = oauth2.authorize_button(
        "Login with Microsoft",
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

### Critical Requirements:
1. **Install the Fixed Fork** (even if you have 0.1.14):
```bash
pip uninstall streamlit-oauth
pip install git+https://github.com/bfortuner/streamlit-oauth
```

2. **.env File Format**:
```env
AUTHORIZE_URL=login.microsoftonline.com/e741d71c-c6b6-47b0-803c-0f3b32b07556/oauth2/v2.0/authorize
TOKEN_URL=login.microsoftonline.com/e741d71c-c6b6-47b0-803c-0f3b32b07556/oauth2/v2.0/token
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
REDIRECT_URI=http://localhost:8501
SCOPE=openid profile email
```

### Key Fixes:
1. Added custom request handler to bypass URL path conversion
2. Modified OAuth URLs to prevent filesystem path interpretation
3. Proper component path handling
4. Monkey-patched Streamlit's component handler
5. Removed protocol prefix from URLs

This should resolve the file path error while maintaining Microsoft Entra ID compatibility. The error occurs because the library tries to resolve URL paths as local filesystem paths, which is incorrect for cloud OAuth providers. The custom handler bypasses this behavior for OAuth endpoints.
