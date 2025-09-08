"""
Sample Anthropic/Claude Custom Connector Manifest Endpoint

This endpoint serves a manifest required by Claude Desktop App and other Claude ecosystem clients for Connector discovery and handshake.
Adapt the fields to your MCP server's configuration and ensure endpoint is accessible at /.well-known/anthropic-connector-manifest.

Reference: Based on known requirements and examples from public connectors.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/.well-known/anthropic-connector-manifest")
async def anthropic_connector_manifest(request: Request):
    manifest = {
        "name": "Google Workspace MCP",
        "description": "Remote MCP for Claude Custom Connector",
        "endpoints": {
            "connect": f"{request.base_url}connect",
            "configure": f"{request.base_url}configure"
        },
        "transport": ["sse", "http"],  # List supported transports
        "oauth": True,
        "sse": True,
        "icon_url": f"{request.base_url}static/icon.png",  # optional, branding
        "documentation_url": "https://github.com/jcmrs/google-workspace-remote-vercel",
        "scopes": ["email", "calendar", "drive", "docs"],  # adjust as needed
        "version": "1.0.0"
        # Add other required fields as per latest documentation
    }
    return JSONResponse(content=manifest)