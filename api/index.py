"""
Vercel serverless function entry point for Google Workspace MCP Server
"""
import os
import sys
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure basic logging for Vercel
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import and configure the MCP server
os.environ.setdefault('WORKSPACE_MCP_BASE_URI', 'https://your-vercel-app.vercel.app')
os.environ.setdefault('WORKSPACE_MCP_PORT', '443')
os.environ.setdefault('OAUTHLIB_INSECURE_TRANSPORT', 'false')  # HTTPS on Vercel
os.environ.setdefault('WORKSPACE_MCP_STATELESS_MODE', 'true')  # Use stateless mode for serverless

# Import after environment setup
from auth.oauth_config import reload_oauth_config
from core.server import server, set_transport_mode, configure_server_for_http
from core.tool_registry import set_enabled_tools as set_enabled_tool_names, wrap_server_tool_method, filter_server_tools

# Reload OAuth config with new environment
reload_oauth_config()

# Import all tool modules
try:
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
except ImportError as e:
    logger.error(f"Failed to import tool modules: {e}")
    raise

# Configure server for HTTP transport
set_transport_mode('streamable-http')
configure_server_for_http()
wrap_server_tool_method(server)

# Set enabled tools (all tools by default)
from auth.scopes import set_enabled_tools
set_enabled_tools(['gmail', 'drive', 'calendar', 'docs', 'sheets', 'chat', 'forms', 'slides', 'tasks', 'search'])

# Get the FastAPI app from the server
app = server.create_fastapi_app()

logger.info("Google Workspace MCP Server initialized for Vercel")

# Export the app for Vercel
# Vercel automatically detects FastAPI/ASGI apps
handler = app
