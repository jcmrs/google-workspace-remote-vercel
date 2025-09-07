# 🚀 Vercel Deployment Instructions

## Quick Deploy Steps

### Option 1: Vercel CLI (Recommended)
1. **Install Vercel CLI** (if not installed):
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy from this directory**:
   ```bash
   cd "C:\Users\jcmei\Documents\CLAUDE\google-workspace-remote-vercel"
   vercel --prod
   ```

### Option 2: GitHub + Vercel Integration
1. **Create GitHub repository** for this folder
2. **Push code** to GitHub
3. **Import to Vercel** via vercel.com dashboard
4. **Auto-deploy** on git push

## 📋 Required Environment Variables

Set these in Vercel Dashboard → Settings → Environment Variables:

```
GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret
WORKSPACE_MCP_BASE_URI=https://your-vercel-app.vercel.app
WORKSPACE_MCP_PORT=443
OAUTHLIB_INSECURE_TRANSPORT=false
WORKSPACE_MCP_STATELESS_MODE=true
MCP_ENABLE_OAUTH21=true
USER_GOOGLE_EMAIL=your-email@gmail.com
```

## 🔄 After Deployment

1. **Note your Vercel URL**: `https://your-app-name.vercel.app`
2. **Update OAuth redirect URIs** in Google Cloud Console:
   - Add: `https://your-app-name.vercel.app/oauth2callback`
3. **Test MCP endpoint**: `https://your-app-name.vercel.app/sse`

## 🎯 Claude Configuration

### Desktop/Local:
```json
{
  "mcpServers": {
    "google-workspace-remote-vercel": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://your-app-name.vercel.app/sse"
      ]
    }
  }
}
```

### Mobile (via claude.ai):
- Settings → Connectors → Add Custom Connector
- URL: `https://your-app-name.vercel.app/sse`
- Name: "Google Workspace Remote Vercel"

---

**✅ READY FOR DEPLOYMENT!**

All files are configured and ready. The deployment will give you a working remote MCP server with your color-coding functionality accessible from all Claude platforms.
