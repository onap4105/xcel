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


The `400 Bad Request` error when requesting an access token from Microsoft's OAuth endpoint typically indicates an issue with the parameters sent in the token request. Here's how to diagnose and fix this:

---

### **1. Check Token Request Parameters**
Microsoft's `/token` endpoint is strict about parameter formatting. Verify these key elements:

#### **a. Client ID & Secret**
- Ensure the `client_id` and `client_secret` match the values from your [Azure AD App Registration](https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade).
- **Common Mistake**: Secrets expire! Regenerate if needed.

#### **b. Redirect URI**
- The `redirect_uri` in the token request **must exactly match** the one registered in Azure AD (including trailing slashes and protocol).
- Example: If registered as `http://localhost:8501/oauth/callback`, ensure it’s identical in your code.

#### **c. Authorization Code**
- The `code` parameter must be the valid authorization code returned by Microsoft after the user logs in.
- **Common Issues**:
  - Using an expired code (codes are short-lived).
  - Reusing a code (codes are single-use).

#### **d. Scope**
- Scopes must be properly formatted and pre-configured in Azure AD.
  - Example: `https://graph.microsoft.com/.default` (for delegated permissions).
  - Avoid mixing v1 and v2 scopes (e.g., `User.Read` vs `https://graph.microsoft.com/User.Read`).

#### **e. Grant Type**
- Ensure `grant_type=authorization_code` is included.

---

### **2. Debugging Steps**
#### **a. Log the Full Token Request**
Add logging to inspect the exact parameters sent to Microsoft:
```python
import logging
logging.basicConfig(level=logging.DEBUG)  # Enable HTTPX debug logs

# Your OAuth code...
```

#### **b. Capture the Full Error Response**
Microsoft often returns a JSON error description. Modify your code to extract it:
```python
from httpx_oauth.oauth2 import OAuth2Error

try:
    result = oauth2.authorize_button("Authorize", REDIRECT_URI, SCOPE)
except OAuth2Error as e:
    if e.response:
        st.error(f"Error details: {e.response.json()}")  # Microsoft's error message
    else:
        st.error(f"Error: {str(e)}")
```

---

### **3. Common Fixes**
#### **a. Update Azure AD App Registration**
1. Go to **Azure Portal > App Registrations > Your App > Authentication**:
   - Add `http://localhost:8501/oauth/callback` under **Redirect URIs**.
   - Enable **ID tokens** and **Access tokens** under **Implicit grant**.

2. Under **API Permissions**:
   - Add required permissions (e.g., `User.Read` for Microsoft Graph).

#### **b. Use the Correct Token Endpoint**
Ensure your token endpoint URL includes the tenant ID:
```python
TOKEN_ENDPOINT = "https://login.microsoftonline.com/e741d71c-c6b6-47b0-803c-0f3b32b07556/oauth2/v2.0/token"
```
Replace `e741d71c-c6b6-47b0-803c-0f3b32b07556` with your actual tenant ID.

#### **c. Validate Scope Format**
For Microsoft Identity Platform (v2.0), use:
```python
SCOPE = ["https://graph.microsoft.com/.default"]  # Delegated permissions
# OR
SCOPE = ["https://graph.microsoft.com/User.Read"]  # Specific scope
```

#### **d. PKCE (Code Verifier)**
If using PKCE (recommended), ensure the `code_verifier` is included:
```python
result = oauth2.authorize_button(
    "Authorize",
    REDIRECT_URI,
    SCOPE,
    extras_params={"code_challenge_method": "S256"},  # Enable PKCE
)
```

---

### **4. Example Working Configuration**
```python
from streamlit_oauth import OAuth2Component
import streamlit as st

CLIENT_ID = "your-azure-client-id"
CLIENT_SECRET = "your-azure-client-secret"
AUTHORIZE_ENDPOINT = "https://login.microsoftonline.com/e741d71c-c6b6-47b0-803c-0f3b32b07556/oauth2/v2.0/authorize"
TOKEN_ENDPOINT = "https://login.microsoftonline.com/e741d71c-c6b6-47b0-803c-0f3b32b07556/oauth2/v2.0/token"
REDIRECT_URI = "http://localhost:8501/oauth/callback"
SCOPE = ["https://graph.microsoft.com/.default"]

oauth2 = OAuth2Component(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    authorize_endpoint=AUTHORIZE_ENDPOINT,
    token_endpoint=TOKEN_ENDPOINT,
)

try:
    result = oauth2.authorize_button(
        "Authorize",
        REDIRECT_URI,
        SCOPE,
        extras_params={
            "prompt": "consent",  # Force consent screen
        },
    )
    if result and "token" in result:
        st.success("Login successful!")
except Exception as e:
    st.error(f"Login failed: {str(e)}")
```

---

### **5. Troubleshooting Checklist**
| Issue                          | Solution                                  |
|---------------------------------|-------------------------------------------|
| Invalid `client_id`/`secret`   | Regenerate in Azure AD                    |
| Mismatched `redirect_uri`      | Update Azure AD and code to match exactly |
| Expired or reused `code`       | Ensure codes are fresh and single-use     |
| Incorrect `scope` format       | Use v2.0 scopes (e.g., `.default`)        |
| Missing `grant_type`           | Add `grant_type=authorization_code`       |

If the error persists, check the **Azure AD Audit Logs** for detailed error context.
