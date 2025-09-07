"""
Vercel serverless function entry point for Google Workspace MCP Server
Uses the original FastMCP implementation with proper MCP protocol support
"""
import os
import sys
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging for Vercel
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set environment variables for Vercel deployment
os.environ.setdefault('WORKSPACE_MCP_BASE_URI', 'https://google-workspace-remote-vercel.vercel.app')
os.environ.setdefault('WORKSPACE_MCP_PORT', '443')
os.environ.setdefault('OAUTHLIB_INSECURE_TRANSPORT', 'false')
os.environ.setdefault('WORKSPACE_MCP_STATELESS_MODE', 'true')
os.environ.setdefault('MCP_ENABLE_OAUTH21', 'true')

try:
    # Import the original MCP server components
    from auth.oauth_config import reload_oauth_config
    from core.server import server, set_transport_mode, configure_server_for_http
    from core.tool_registry import set_enabled_tools as set_enabled_tool_names, wrap_server_tool_method, filter_server_tools
    
    # Reload OAuth config with Vercel environment
    reload_oauth_config()
    
    # Import all tool modules to register them
    import gmail.gmail_tools
    import gdrive.drive_tools
    import gcalendar.calendar_tools
    import gdocs.docs_tools
    import gsheets.sheets_tools
    import gchat.chat_tools
    import gforms.forms_tools
    import gslides.slides_tools
    import gtasks.tasks_tools
    import gsearch.search_tools
    
    logger.info("All tool modules imported successfully")
    
    # Configure server for HTTP transport
    set_transport_mode('streamable-http')
    configure_server_for_http()
    wrap_server_tool_method(server)
    
    # Set enabled tools (all tools by default)
    from auth.scopes import set_enabled_tools
    set_enabled_tools(['gmail', 'drive', 'calendar', 'docs', 'sheets', 'chat', 'forms', 'slides', 'tasks', 'search'])
    
    # Create the FastAPI app using the original server
    app = server.create_fastapi_app()
    
    logger.info("Google Workspace MCP Server initialized for Vercel with FastMCP")
    
except Exception as e:
    logger.error(f"Failed to initialize MCP server: {e}")
    # Fallback to basic FastAPI for debugging
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    app = FastAPI(title="Google Workspace MCP Server - Fallback Mode")
    
    @app.get("/")
    def fallback_root():
        return {
            "service": "Google Workspace MCP Server",
            "status": "fallback_mode",
            "error": str(e),
            "message": "MCP server failed to initialize, running in fallback mode"
        }
    
    @app.get("/health")
    def fallback_health():
        return {"status": "fallback", "error": str(e)}

# Export for Vercel
handler = app
