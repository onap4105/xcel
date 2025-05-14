The error during OAuth login in Streamlit (`streamlit-oauth`) often stems from misconfiguration of redirect URIs, session/cookie handling, or CORS policies. Here’s a structured approach to resolve it:

---

### **1. Check Redirect URI Configuration**
Most OAuth providers (Google, GitHub, etc.) require **exact matching** of redirect URIs.  
**Steps**:
1. Ensure your redirect URI in the OAuth provider’s settings matches the callback URL of your Streamlit app.  
   - For local testing: `http://localhost:8501/oauth/callback`  
   - For production: `https://<your-domain>/oauth/callback`  
2. For `streamlit-oauth`, explicitly set the `redirect_uri` during initialization:
   ```python
   from streamlit_oauth import OAuth2Component

   oauth = OAuth2Component(
       client_id="...",
       client_secret="...",
       authorize_endpoint="...",
       token_endpoint="...",
       refresh_token_endpoint="...",
       revoke_token_endpoint="...",
       redirect_uri="http://localhost:8501/oauth/callback"  # Match provider settings
   )
   ```

---

### **2. Handle CORS and Session State**
Streamlit’s session state may lose context during OAuth redirects.  
**Fix**:
1. Ensure the `state` parameter is persisted and validated:
   ```python
   # Generate a random state token and store it in session state
   if 'oauth_state' not in st.session_state:
       st.session_state.oauth_state = secrets.token_hex(16)

   result = oauth.authorize_button(
       name="Login",
       redirect_uri=redirect_uri,
       scope="openid email profile",
       key="oauth",
       extras_params={"state": st.session_state.oauth_state}
   )

   if result and 'token' in result:
       # Validate the returned `state` matches st.session_state.oauth_state
       if result.get('state') != st.session_state.oauth_state:
           st.error("Invalid state token")
           return
       st.session_state.token = result.get('token')
   ```

---

### **3. Configure OAuth Provider Settings**
For **Google OAuth** (example):
1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials) > your OAuth client ID.  
2. Add authorized redirect URIs:  
   - `http://localhost:8501/oauth/callback` (local)  
   - `https://<your-domain>/oauth/callback` (production)  

---

### **4. Debugging Steps**
1. **Check Browser Console**: Look for CORS errors or network failures.  
2. **Test in Incognito Mode**: Cached credentials/sessions might interfere.  
3. **Log Output**: Print the OAuth result and error details:
   ```python
   if result:
       st.write(result)  # Inspect the returned object
   if result and 'error' in result:
       st.error(f"Error: {result.get('error')}: {result.get('error_description')}")
   ```

---

### **5. Example Working Snippet**
```python
import streamlit as st
from streamlit_oauth import OAuth2Component
import secrets

CLIENT_ID = "your-client-id"
CLIENT_SECRET = "your-client-secret"
AUTHORIZE_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
REDIRECT_URI = "http://localhost:8501/oauth/callback"

# Initialize OAuth2Component
oauth = OAuth2Component(
    CLIENT_ID, CLIENT_SECRET,
    AUTHORIZE_ENDPOINT,
    TOKEN_ENDPOINT,
    TOKEN_ENDPOINT,  # Refresh token endpoint (if needed)
    TOKEN_ENDPOINT,  # Revoke token endpoint (if needed)
    redirect_uri=REDIRECT_URI
)

# Generate state token
if 'oauth_state' not in st.session_state:
    st.session_state.oauth_state = secrets.token_hex(16)

# Login button
result = oauth.authorize_button(
    "Login with Google",
    REDIRECT_URI,
    scope="openid email profile",
    key="google",
    extras_params={
        "state": st.session_state.oauth_state,
        "prompt": "consent",  # Force re-authentication
        "access_type": "offline"
    }
)

# Handle result
if result:
    if 'error' in result:
        st.error(f"Error: {result['error']}")
    else:
        st.session_state.token = result['token']
        st.success("Logged in successfully!")
```

---

### **Common Fixes Summary**
| Issue                  | Solution                                  |
|-------------------------|-------------------------------------------|
| Redirect URI mismatch  | Update provider settings to match exactly |
| Invalid state token    | Persist `state` in session                |
| CORS errors            | Ensure backend allows Streamlit’s origin  |
| Silent auth failure    | Add `prompt=consent` to force login       |

If the issue persists, share the **exact error message** from the browser console or Streamlit logs.
