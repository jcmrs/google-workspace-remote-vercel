from http.server import BaseHTTPRequestHandler
import json
import urllib.parse

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the path
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # Debug - always show what path we're getting
        debug_info = {
            "received_path": path,
            "full_url": self.path,
            "parsed_path": str(parsed_path)
        }
        
        # Test if this is the manifest path
        if path == '/.well-known/anthropic-connector-manifest':
            manifest = {
                "name": "Google Workspace MCP",
                "description": "Remote MCP server for Google Workspace integration with Claude",
                "version": "1.0.0",
                "debug": "MANIFEST_ENDPOINT_WORKING"
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(manifest).encode())
            return
        
        # Default response with debug info
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "debug": debug_info,
            "message": "Debug endpoint - checking path matching"
        }
        
        self.wfile.write(json.dumps(response).encode())
        return
