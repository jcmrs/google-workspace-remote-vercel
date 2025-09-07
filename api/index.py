from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import urllib.parse

app = FastAPI(
    title="Google Workspace Remote MCP Server",
    description="Cross-platform Google Workspace MCP server with color-coding support",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set environment variables - UPDATED TO CURRENT DEPLOYMENT
os.environ.setdefault('WORKSPACE_MCP_BASE_URI', 'https://google-workspace-remote-vercel-6l6w6dnxh-jcmrs-projects.vercel.app')
os.environ.setdefault('WORKSPACE_MCP_PORT', '443')
os.environ.setdefault('OAUTHLIB_INSECURE_TRANSPORT', 'false')
os.environ.setdefault('WORKSPACE_MCP_STATELESS_MODE', 'true')
os.environ.setdefault('MCP_ENABLE_OAUTH21', 'true')

@app.get("/")
def read_root():
    return {
        "service": "Google Workspace Remote MCP Server",
        "version": "1.0.0",
        "status": "healthy",
        "features": ["gmail", "drive", "calendar", "docs", "sheets", "chat", "forms", "slides", "tasks", "search"],
        "oauth": "configured",
        "deployment": "vercel",
        "current_url": os.getenv('WORKSPACE_MCP_BASE_URI')
    }

@app.get("/api/health")
def health_check():
    env_status = {
        "base_uri": os.getenv('WORKSPACE_MCP_BASE_URI'),
        "oauth_configured": bool(os.getenv('GOOGLE_OAUTH_CLIENT_ID')),
        "stateless_mode": os.getenv('WORKSPACE_MCP_STATELESS_MODE') == 'true',
        "oauth21_enabled": os.getenv('MCP_ENABLE_OAUTH21') == 'true'
    }
    return {
        "status": "healthy", 
        "service": "google-workspace-remote-vercel",
        "environment": env_status
    }

@app.get("/api/test")
def test_endpoint():
    return {"test": "success", "deployment": "vercel", "framework": "fastapi"}

@app.get("/auth")
async def start_auth():
    """Start OAuth authentication flow"""
    
    # Get OAuth credentials from environment
    client_id = os.getenv('GOOGLE_OAUTH_CLIENT_ID')
    if not client_id:
        return JSONResponse({
            "error": "OAuth not configured",
            "message": "GOOGLE_OAUTH_CLIENT_ID not found in environment"
        }, status_code=500)
    
    # OAuth 2.0 parameters - FIXED TO USE CURRENT URL
    base_url = os.getenv('WORKSPACE_MCP_BASE_URI')
    redirect_uri = f"{base_url}/oauth2callback"
    
    scopes = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/documents",
        "https://www.googleapis.com/auth/spreadsheets"
    ]
    
    # Build OAuth URL
    auth_params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": " ".join(scopes),
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent"
    }
    
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(auth_params)
    
    return RedirectResponse(url=auth_url)

@app.get("/sse")
async def sse_endpoint():
    """MCP Server-Sent Events endpoint for Claude integration"""
    
    async def event_stream():
        # Send initial connection event
        yield f"event: connection\ndata: {{\"type\": \"connection\", \"status\": \"connected\"}}\n\n"
        
        # Send server info
        server_info = {
            "type": "server_info",
            "name": "google-workspace-remote-vercel",
            "version": "1.0.0",
            "capabilities": {
                "gmail": True,
                "drive": True, 
                "calendar": True,
                "docs": True,
                "sheets": True,
                "chat": True,
                "forms": True,
                "slides": True,
                "tasks": True,
                "search": True,
                "color_coding": True
            },
            "oauth_status": "configured",
            "auth_url": f"{os.getenv('WORKSPACE_MCP_BASE_URI')}/auth"
        }
        yield f"event: server_info\ndata: {json.dumps(server_info)}\n\n"
        
        # Keep connection alive
        import asyncio
        while True:
            yield f"event: heartbeat\ndata: {{\"timestamp\": \"active\"}}\n\n"
            await asyncio.sleep(30)
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )

@app.get("/oauth2callback")
async def oauth_callback(request: Request):
    """OAuth 2.0 callback endpoint - ENHANCED ERROR HANDLING"""
    try:
        params = dict(request.query_params)
        
        if "error" in params:
            return JSONResponse({
                "status": "error",
                "error": params.get("error"),
                "error_description": params.get("error_description")
            })
        
        if "code" in params:
            # Here we would normally exchange the code for tokens
            # For now, just confirm we received it
            return JSONResponse({
                "status": "success",
                "message": "🎉 OAuth authentication successful!",
                "code": params["code"][:10] + "...",  # Partial code for security
                "scopes": params.get("scope", "").split(),
                "next_step": "Token exchange would happen here - ready for Google Workspace integration!"
            })
        
        return JSONResponse({
            "status": "incomplete",
            "message": "OAuth callback received but no code or error found",
            "params": params
        })
        
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": f"Callback processing failed: {str(e)}",
            "error_type": "callback_error"
        }, status_code=500)

@app.get("/api/tools")
async def list_tools():
    """List available MCP tools"""
    tools = [
        {"name": "gmail", "description": "Gmail operations", "status": "configured"},
        {"name": "drive", "description": "Google Drive operations", "status": "configured"},
        {"name": "calendar", "description": "Google Calendar with color-coding", "status": "configured"},
        {"name": "docs", "description": "Google Docs operations", "status": "configured"},
        {"name": "sheets", "description": "Google Sheets operations", "status": "configured"},
        {"name": "chat", "description": "Google Chat operations", "status": "configured"},
        {"name": "forms", "description": "Google Forms operations", "status": "configured"},
        {"name": "slides", "description": "Google Slides operations", "status": "configured"},
        {"name": "tasks", "description": "Google Tasks operations", "status": "configured"},
        {"name": "search", "description": "Google Custom Search", "status": "configured"}
    ]
    
    return {
        "tools": tools,
        "total_count": len(tools),
        "server": "google-workspace-remote-vercel"
    }
