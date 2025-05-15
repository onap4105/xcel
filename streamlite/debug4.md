The error occurs because the `streamlit-oauth` component is trying to access a local file path that's being incorrectly constructed from your OAuth endpoint URLs. Here's how to fix it:

### Modified OAuth Configuration Section:
```python
# --- OAuth Configuration ---
# Use explicit parameter names and proper endpoint configuration
oauth2 = OAuth2Component(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    authorize_endpoint=AUTHORIZE_URL,
    token_endpoint=TOKEN_URL,
    refresh_token_endpoint=REFRESH_TOKEN_URL or None,
    revoke_token_endpoint=REVOKE_TOKEN_URL or None,
    client_kwargs={
        "scope": SCOPE,
        "redirect_uri": REDIRECT_URI
    }
)
```

### Required Fixes:
1. **Package Version Compatibility**:
   ```bash
   pip uninstall streamlit-oauth
   pip install git+https://github.com/bfortuner/streamlit-oauth
   ```

2. **Microsoft Entra ID Specific Configuration**:
   Add this after loading environment variables:
   ```python
   # Clean up Azure AD URLs
   AUTHORIZE_URL = AUTHORIZE_URL.replace("https://", "")
   TOKEN_URL = TOKEN_URL.replace("https://", "")
   ```

3. **Frontend Path Workaround**:
   Add this at the top of your script:
   ```python
   import sys
   sys.path.append(r"c:\Users\hg4105\myworkspace\streamlit\.venv\Lib\site-packages\streamlit_oauth\frontend\dist")
   ```

### Why This Happens:
The error shows the library is trying to resolve your OAuth endpoints as local file paths due to:
1. Incorrect parameter naming in component initialization
2. Special characters in Microsoft Entra ID URLs (`://` being converted to filesystem paths)
3. Missing frontend assets in the package installation

### Additional Verification Steps:
1. Check your `.env` file contains PROPERLY FORMATTED URLs:
   ```env
   AUTHORIZE_URL=login.microsoftonline.com/e741d71c-c6b6-47b0-803c-0f3b32b07556/oauth2/v2.0/authorize
   TOKEN_URL=login.microsoftonline.com/e741d71c-c6b6-47b0-803c-0f3b32b07556/oauth2/v2.0/token
   REDIRECT_URI=http://localhost:8501  # Must match Azure AD registration
   ```

2. Verify directory structure exists:
   ```python
   # Add this check after environment variables
   frontend_path = Path(r"c:\Users\hg4105\myworkspace\streamlit\.venv\Lib\site-packages\streamlit_oauth\frontend\dist")
   if not frontend_path.exists():
       st.error(f"Missing frontend assets at: {frontend_path}")
       st.stop()
   ```

This solution addresses both the path resolution issue and Microsoft Entra ID's specific URL formatting requirements. The error should resolve after these changes.
