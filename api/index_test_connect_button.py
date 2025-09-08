from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.parse
import secrets
import string

# Test version: Remove oauth: true and configure endpoint to trigger Connect button

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the path
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # Anthropic Connector Manifest - SIMPLIFIED VERSION
        if path == '/.well-known/anthropic-connector-manifest':
            try:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                base_url = "https://google-workspace-remote-vercel.vercel.app"
                # SIMPLIFIED MANIFEST - Remove oauth: true and configure endpoint
                manifest = {
                    "name": "Google Workspace Remote MCP",
                    "description": "Remote MCP server for Google Workspace integration with Claude",
                    "version": "1.0.0",
                    "endpoints": {
                        "connect": f"{base_url}/connect"
                        # Removed "configure" endpoint
                    },
                    "transport": ["http"],
                    # Removed "oauth": True
                    "icon_url": f"{base_url}/static/icon.png",
                    "documentation_url": "https://github.com/jcmrs/google-workspace-remote-vercel",
                    "scopes": ["email", "calendar", "drive", "docs", "sheets", "slides", "forms", "chat", "tasks"],
                    "features": [
                        "Gmail", "Calendar", "Drive", "Docs", "Sheets", 
                        "Slides", "Forms", "Chat", "Tasks", "Search"
                    ],
                    "debug": "test_connect_button_simplified_manifest"
                }
                
                manifest_json = json.dumps(manifest)
                self.wfile.write(manifest_json.encode())
                return
            except Exception as e:
                # If manifest fails, return error info
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                error_response = {"error": str(e), "path": path, "debug": "manifest_exception"}
                self.wfile.write(json.dumps(error_response).encode())
                return
        
        # Connect endpoint - returns simple connection info
        if path == '/connect':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Simple response - no OAuth configuration
            connect_response = {
                "status": "ready",
                "service": "Google Workspace Remote MCP",
                "message": "Simplified manifest test - Connect button should appear",
                "debug": "no_oauth_declared"
            }
            
            self.wfile.write(json.dumps(connect_response).encode())
            return
        
        # Default GET response - service info
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "service": "Google Workspace MCP Server - TEST VERSION",
            "version": "1.0.0", 
            "status": "testing_connect_button",
            "message": "Simplified manifest to test Connect vs Configure button behavior",
            "debug": "oauth_and_configure_endpoint_removed"
        }
        
        self.wfile.write(json.dumps(response).encode())
        return
    
    def do_OPTIONS(self):
        # Handle CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        return
