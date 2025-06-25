# 🔒 Security Guide for Google Sheets API Integration

## ⚠️ CRITICAL SECURITY WARNING

**NEVER** commit or share these files publicly:
- `credentials.json` - Contains OAuth client secrets
- `token.json` - Contains access tokens
- `.env` - Contains API keys

## 🚨 What's at Risk

### `credentials.json` contains:
- OAuth 2.0 client ID and secret
- Authorized redirect URIs
- Google Cloud project information

### If exposed, attackers could:
- Make API requests on your behalf
- Access your Google Sheets data
- Potentially access other Google services
- Generate charges on your Google Cloud account

## ✅ Security Best Practices

### 1. File Protection
```bash
# Set restrictive permissions (Linux/Mac)
chmod 600 credentials.json
chmod 600 token.json
chmod 600 .env

# Windows equivalent
icacls credentials.json /grant:r "%USERNAME%:R"
```

### 2. Git Protection
Your `.gitignore` now includes:
```gitignore
# Google Sheets API credentials (NEVER commit these!)
credentials.json
token.json
```

### 3. Environment Variables (Recommended)
Instead of `credentials.json`, use environment variables:

Add to your `.env` file:
```env
# Google Sheets Configuration (Base64 encoded)
GOOGLE_CREDENTIALS_BASE64=eyJ0eXBlIjoic2VydmljZV9hY2NvdW50...
# Or individual fields
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
```

### 4. Service Account (Production)
For production use, create a service account instead:
1. Go to Google Cloud Console
2. IAM & Admin > Service Accounts
3. Create service account with minimal permissions
4. Download JSON key file
5. Store securely and reference via environment variable

## 🔧 Secure Implementation Options

### Option 1: Environment-based Credentials
```python
import os
import json
import base64
from google.oauth2.credentials import Credentials

def get_credentials_from_env():
    """Load credentials from environment variables"""
    creds_b64 = os.getenv('GOOGLE_CREDENTIALS_BASE64')
    if creds_b64:
        creds_data = json.loads(base64.b64decode(creds_b64))
        return Credentials.from_authorized_user_info(creds_data)
    return None
```

### Option 2: Service Account (Recommended for Production)
```python
from google.oauth2 import service_account

def get_service_account_credentials():
    """Use service account for production"""
    key_path = os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY_PATH')
    if key_path and os.path.exists(key_path):
        return service_account.Credentials.from_service_account_file(
            key_path, scopes=SCOPES
        )
    return None
```

## 🎯 Current Setup Recommendations

### For Development:
1. ✅ Keep `credentials.json` local only
2. ✅ Use `.gitignore` to prevent commits
3. ✅ Set restrictive file permissions
4. ✅ Delete from shared drives/cloud storage

### For Production:
1. 🔄 Switch to service account authentication
2. 🔄 Use environment variables for configuration
3. 🔄 Implement credential rotation
4. 🔄 Use Google Cloud Secret Manager

## 🚨 If Credentials Are Compromised

### Immediate Actions:
1. **Revoke the OAuth client** in Google Cloud Console
2. **Generate new credentials** with different client ID
3. **Check Google Cloud audit logs** for unauthorized usage
4. **Review billing** for unexpected charges
5. **Rotate all related API keys**

### Prevention:
- Regular credential rotation
- Monitor API usage
- Use least-privilege access
- Enable audit logging

## 📋 Security Checklist

- [ ] `credentials.json` is in `.gitignore`
- [ ] File permissions are restrictive (600)
- [ ] No credentials in code repositories
- [ ] Environment variables used where possible
- [ ] Service account ready for production
- [ ] Monitoring enabled for API usage
- [ ] Backup plan for credential compromise

## 🔗 Resources

- [Google Cloud Security Best Practices](https://cloud.google.com/security/best-practices)
- [OAuth 2.0 Security Best Practices](https://tools.ietf.org/html/draft-ietf-oauth-security-topics)
- [Google Sheets API Security](https://developers.google.com/sheets/api/guides/authorizing)
