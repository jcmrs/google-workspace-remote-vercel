"""
Simplified Vercel serverless function entry point for Google Workspace MCP Server
"""
import os
import sys
import logging
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure basic logging for Vercel
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a simple FastAPI app for testing
app = FastAPI(title="Google Workspace MCP Server", version="1.0.0")

@app.get("/")
async def root():
    """Root endpoint for health check"""
    return {"status": "healthy", "service": "Google Workspace MCP Server", "version": "1.0.0"}

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "timestamp": "2025-09-07"}

@app.get("/sse")
async def sse_endpoint():
    """MCP SSE endpoint placeholder"""
    return {"message": "MCP SSE endpoint", "status": "configured"}

@app.get("/oauth2callback")
async def oauth_callback(request: Request):
    """OAuth callback endpoint placeholder"""
    return {"message": "OAuth callback", "query_params": dict(request.query_params)}

# Try to import and initialize the full MCP server
try:
    # Set environment variables first
    os.environ.setdefault('WORKSPACE_MCP_BASE_URI', 'https://google-workspace-remote-vercel-oia6069ub-jcmrs-projects.vercel.app')
    os.environ.setdefault('WORKSPACE_MCP_PORT', '443')
    os.environ.setdefault('OAUTHLIB_INSECURE_TRANSPORT', 'false')
    os.environ.setdefault('WORKSPACE_MCP_STATELESS_MODE', 'true')
    
    # Import MCP components
    from auth.oauth_config import reload_oauth_config
    reload_oauth_config()
    
    logger.info("Basic MCP configuration loaded successfully")
    
    # Try to import the full server
    from core.server import server, set_transport_mode, configure_server_for_http
    from core.tool_registry import wrap_server_tool_method
    
    # Configure for HTTP transport
    set_transport_mode('streamable-http')
    configure_server_for_http()
    wrap_server_tool_method(server)
    
    # Get the full MCP FastAPI app
    mcp_app = server.create_fastapi_app()
    
    # Mount the MCP app
    app.mount("/mcp", mcp_app)
    
    logger.info("Full MCP server mounted successfully")
    
except Exception as e:
    logger.error(f"Failed to initialize full MCP server: {e}")
    logger.info("Running in simplified mode with basic endpoints only")

# Export the app for Vercel
handler = app

logger.info("Google Workspace MCP Server (Simplified) initialized for Vercel")
