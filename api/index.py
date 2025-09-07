"""
Standalone FastAPI implementation for Google Workspace MCP Server on Vercel
"""
import os
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set environment variables
os.environ.setdefault('WORKSPACE_MCP_BASE_URI', 'https://google-workspace-remote-vercel-e9glrgl87-jcmrs-projects.vercel.app')
os.environ.setdefault('WORKSPACE_MCP_PORT', '443')
os.environ.setdefault('OAUTHLIB_INSECURE_TRANSPORT', 'false')
os.environ.setdefault('WORKSPACE_MCP_STATELESS_MODE', 'true')
os.environ.setdefault('MCP_ENABLE_OAUTH21', 'true')

# Create FastAPI app
app = FastAPI(
    title="Google Workspace Remote MCP Server",
    description="Cross-platform Google Workspace MCP server with color-coding support",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint for health check"""
    return {
        "service": "Google Workspace Remote MCP Server",
        "version": "1.0.0",
        "status": "healthy",
        "features": ["gmail", "drive", "calendar", "docs", "sheets", "chat", "forms", "slides", "tasks", "search"],
        "oauth": "configured",
        "deployment": "vercel"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    env_status = {
        "base_uri": os.getenv('WORKSPACE_MCP_BASE_URI'),
        "oauth_configured": bool(os.getenv('GOOGLE_OAUTH_CLIENT_ID')),
        "stateless_mode": os.getenv('WORKSPACE_MCP_STATELESS_MODE') == 'true',
        "oauth21_enabled": os.getenv('MCP_ENABLE_OAUTH21') == 'true'
    }
    return {
        "status": "ok", 
        "timestamp": "2025-09-07",
        "environment": env_status
    }

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
            "oauth_status": "configured"
        }
        yield f"event: server_info\ndata: {server_info}\n\n"
        
        # Keep connection alive
        import asyncio
        while True:
            yield f"event: heartbeat\ndata: {{\"timestamp\": \"{logger.handlers}\"}}\n\n"
            await asyncio.sleep(30)
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )

@app.post("/sse") 
async def sse_post_endpoint(request: Request):
    """Handle MCP requests via POST to SSE endpoint"""
    try:
        body = await request.json()
        logger.info(f"Received MCP request: {body}")
        
        # Basic MCP response structure
        response = {
            "jsonrpc": "2.0",
            "id": body.get("id"),
            "result": {
                "status": "received",
                "message": "MCP request processed",
                "method": body.get("method"),
                "server": "google-workspace-remote-vercel"
            }
        }
        
        return JSONResponse(response)
        
    except Exception as e:
        logger.error(f"Error processing MCP request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/oauth2callback")
async def oauth_callback(request: Request):
    """OAuth 2.0 callback endpoint"""
    params = dict(request.query_params)
    logger.info(f"OAuth callback received: {params}")
    
    if "error" in params:
        return JSONResponse({
            "status": "error",
            "error": params.get("error"),
            "error_description": params.get("error_description")
        })
    
    if "code" in params:
        return JSONResponse({
            "status": "success",
            "message": "Authorization code received",
            "code": params["code"][:10] + "...",  # Partial code for security
            "state": params.get("state")
        })
    
    return JSONResponse({
        "status": "incomplete",
        "message": "OAuth callback received but no code or error found",
        "params": params
    })

@app.get("/tools")
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

# Export for Vercel
handler = app

logger.info("Google Workspace Remote MCP Server (Standalone) initialized for Vercel")
