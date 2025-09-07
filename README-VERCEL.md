# Google Workspace MCP - Vercel Remote Deployment

This is a **remote MCP server** deployment of the Google Workspace MCP, adapted for Vercel serverless functions. It provides the same functionality as the local version but accessible from mobile Claude and all Claude platforms.

## 🎯 Purpose

- **Cross-platform access**: Use Google Workspace tools from Claude Desktop, Web, and Mobile
- **Color-coded calendar events**: Full support for Google Calendar colorId parameter
- **No local installation**: Serverless deployment on Vercel's free tier

## 🚀 Features

All original Google Workspace MCP features:
- 📅 **Google Calendar** (with color-coding support)
- 📧 **Gmail** 
- 📁 **Google Drive**
- 📄 **Google Docs**
- 📊 **Google Sheets**
- 🖼️ **Google Slides**
- 📝 **Google Forms**
- 💬 **Google Chat**
- ✓ **Google Tasks**
- 🔍 **Google Custom Search**

## 🔧 Deployment Instructions

### 1. Vercel Project Setup
Deploy this repository to Vercel (automatically handled via Claude MCP integration)

### 2. Environment Variables
Configure these in Vercel Dashboard > Settings > Environment Variables:

```
GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret
WORKSPACE_MCP_BASE_URI=https://your-vercel-app.vercel.app
WORKSPACE_MCP_PORT=443
OAUTHLIB_INSECURE_TRANSPORT=false
WORKSPACE_MCP_STATELESS_MODE=true
MCP_ENABLE_OAUTH21=true
```

### 3. Google Cloud Console Setup
Update your OAuth application redirect URIs to include:
```
https://your-vercel-app.vercel.app/oauth2callback
```

### 4. Claude Configuration
Add to your Claude Desktop config OR configure via claude.ai web interface:

```json
{
  "mcpServers": {
    "google-workspace-remote-vercel": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://your-vercel-app.vercel.app/sse"
      ]
    }
  }
}
```

## 📱 Mobile Access

1. Configure via claude.ai web interface:
   - Settings → Connectors → Add Custom Connector
   - URL: `https://your-vercel-app.vercel.app/sse`
   - Name: "Google Workspace Remote"

2. Configuration automatically syncs to mobile apps

## 🎨 Color-Coding Support

This deployment includes the color-coding functionality:
- Create events with specific colors: "Create a meeting tomorrow at 3 PM with color blue"
- Modify event colors: "Change my 3 PM meeting to red"
- Supports all Google Calendar colorId values (1-11)

## 🔒 Security

- OAuth 2.1 with PKCE for enhanced security
- Stateless mode for serverless compatibility
- All credentials stored securely in Vercel environment variables

## ⚡ Performance

- Vercel's global edge network for low latency
- Serverless architecture scales automatically
- Free tier sufficient for typical usage (< 30 operations/day)

## 🛠️ Technical Details

- **Runtime**: Python 3.11+ on Vercel
- **Framework**: FastAPI with FastMCP
- **Transport**: HTTP with Server-Sent Events (SSE)
- **Authentication**: OAuth 2.1 with stateless session management

## 📊 Usage Monitoring

Monitor your usage in Vercel Dashboard to ensure you stay within free tier limits:
- 100,000 serverless function invocations/month
- Typical calendar operations use ~2-3 invocations each

---

**Note**: This is the remote version of the Google Workspace MCP, adapted specifically for cross-platform access including mobile Claude applications.
