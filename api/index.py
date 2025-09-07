"""
Minimal MCP server implementation for Vercel
Based on the MCP protocol specification
"""
import json
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Google Workspace MCP Server")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables
os.environ.setdefault('WORKSPACE_MCP_BASE_URI', 'https://google-workspace-remote-vercel.vercel.app')

@app.get("/")
def root():
    return {
        "service": "Google Workspace MCP Server",
        "version": "1.0.0",
        "status": "minimal_mcp_implementation",
        "protocol": "MCP",
        "transport": "streamable-http"
    }

@app.get("/health")
def health():
    return {"status": "healthy", "implementation": "minimal_mcp"}

# MCP Protocol Implementation
@app.post("/")
async def mcp_handler(request: Request):
    """Handle MCP protocol messages"""
    try:
        data = await request.json()
        
        # MCP Initialize handshake
        if data.get("method") == "initialize":
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": data.get("id"),
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {}
                    },
                    "serverInfo": {
                        "name": "google-workspace-mcp-server",
                        "version": "1.0.0"
                    }
                }
            })
        
        # Tools list
        elif data.get("method") == "tools/list":
            tools = [
                {
                    "name": "gmail_search",
                    "description": "Search Gmail messages",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"}
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "calendar_create_event",
                    "description": "Create a calendar event",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Event title"},
                            "start_time": {"type": "string", "description": "Start time"},
                            "end_time": {"type": "string", "description": "End time"}
                        },
                        "required": ["title", "start_time", "end_time"]
                    }
                },
                {
                    "name": "drive_list_files",
                    "description": "List Google Drive files",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "folder_id": {"type": "string", "description": "Folder ID to search in"}
                        }
                    }
                }
            ]
            
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": data.get("id"),
                "result": {"tools": tools}
            })
        
        # Tool call handler
        elif data.get("method") == "tools/call":
            tool_name = data.get("params", {}).get("name")
            arguments = data.get("params", {}).get("arguments", {})
            
            # Mock tool responses for testing
            if tool_name == "gmail_search":
                result = {
                    "content": [
                        {
                            "type": "text", 
                            "text": f"Gmail search for '{arguments.get('query', '')}' - Authentication required"
                        }
                    ]
                }
            elif tool_name == "calendar_create_event":
                result = {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Calendar event '{arguments.get('title', '')}' would be created - Authentication required"
                        }
                    ]
                }
            elif tool_name == "drive_list_files":
                result = {
                    "content": [
                        {
                            "type": "text",
                            "text": "Drive files would be listed - Authentication required"
                        }
                    ]
                }
            else:
                result = {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Unknown tool: {tool_name}"
                        }
                    ]
                }
            
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": data.get("id"),
                "result": result
            })
        
        # Notifications/initialized
        elif data.get("method") == "notifications/initialized":
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": data.get("id"),
                "result": {}
            })
        
        # Default response
        else:
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": data.get("id"),
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {data.get('method')}"
                }
            })
    
    except Exception as e:
        logger.error(f"MCP handler error: {e}")
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": data.get("id") if "data" in locals() else None,
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        })

# SSE endpoint for MCP Inspector compatibility
@app.get("/sse")
async def sse_endpoint():
    """Server-Sent Events endpoint for MCP"""
    
    async def event_stream():
        # Send initial message
        yield f"data: {json.dumps({'type': 'connection', 'status': 'connected'})}\n\n"
        
        # Send server capabilities
        capabilities = {
            "type": "server_info",
            "name": "google-workspace-mcp-server",
            "version": "1.0.0",
            "capabilities": {
                "tools": True,
                "resources": False
            }
        }
        yield f"data: {json.dumps(capabilities)}\n\n"
        
        # Keep connection alive
        while True:
            await asyncio.sleep(30)
            yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )

# Export for Vercel
handler = app

logger.info("Minimal Google Workspace MCP Server initialized for Vercel")
