from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.parse
import time

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the path
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # OAuth Authorization Server metadata endpoint
        if path == '/.well-known/oauth-authorization-server':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "issuer": "https://google-workspace-remote-vercel.vercel.app",
                "authorization_endpoint": "https://google-workspace-remote-vercel.vercel.app/authorize",
                "token_endpoint": "https://google-workspace-remote-vercel.vercel.app/token",
                "response_types_supported": ["code"],
                "grant_types_supported": ["authorization_code"],
                "code_challenge_methods_supported": ["S256"]
            }
            
            self.wfile.write(json.dumps(response).encode())
            return
        
        # OAuth Protected Resource metadata endpoint (following Vercel pattern)
        # Handle both encoded and unencoded versions of the path
        if path == '/.well-known/oauth-protected-resource' or path == '/.well-known/oauth-protected-resource':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "authorization_servers": [
                    "https://google-workspace-remote-vercel.vercel.app"
                ]
            }
            
            self.wfile.write(json.dumps(response).encode())
            return
        
        # Test: catch all .well-known requests to debug
        if '.well-known' in path:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "debug": "well-known endpoint hit",
                "requested_path": path,
                "authorization_servers": [
                    "https://google-workspace-remote-vercel.vercel.app"
                ]
            }
            
            self.wfile.write(json.dumps(response).encode())
            return
        
        # Debug: Log the path to see what's being requested
        print(f"DEBUG: Requested path: '{path}'")
        
        # SSE endpoint for MCP remote connection
        if path == '/sse':
            self.handle_sse()
            return
        
        # Default GET response
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "service": "Google Workspace MCP Server",
            "version": "1.0.0", 
            "status": "working",
            "protocol": "MCP",
            "endpoint": self.path,
            "transports": ["POST", "SSE"],
            "message": "Vercel Python handler working correctly"
        }
        
        self.wfile.write(json.dumps(response).encode())
        return
    
    def handle_sse(self):
        """Handle Server-Sent Events for MCP protocol"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Connection', 'keep-alive')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Send initial MCP server info
        server_info = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "google-workspace-mcp-server",
                    "version": "1.0.0"
                }
            }
        }
        
        # Send as SSE event
        self.wfile.write(f"data: {json.dumps(server_info)}\n\n".encode())
        self.wfile.flush()
        
        # Send tools list
        tools_data = {
            "jsonrpc": "2.0", 
            "method": "tools/list",
            "params": {
                "tools": [
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
                    }
                ]
            }
        }
        
        self.wfile.write(f"data: {json.dumps(tools_data)}\n\n".encode())
        self.wfile.flush()
        
        # Keep connection alive (basic implementation)
        try:
            for i in range(3):  # Send a few heartbeats then close (Vercel timeout)
                time.sleep(10)
                heartbeat = {"jsonrpc": "2.0", "method": "heartbeat", "params": {"timestamp": int(time.time())}}
                self.wfile.write(f"data: {json.dumps(heartbeat)}\n\n".encode())
                self.wfile.flush()
        except:
            pass  # Connection closed
    
    def do_POST(self):
        # Handle MCP protocol messages via POST (keep existing functionality)
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(post_data)
            
            # MCP Initialize handshake
            if data.get("method") == "initialize":
                response = {
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
                }
            
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
                    }
                ]
                
                response = {
                    "jsonrpc": "2.0",
                    "id": data.get("id"),
                    "result": {"tools": tools}
                }
            
            # Default response for unknown methods
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": data.get("id"),
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {data.get('method')}"
                    }
                }
            
        except Exception as e:
            response = {
                "jsonrpc": "2.0",
                "id": data.get("id") if "data" in locals() else None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
        
        # Send MCP response
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
        return
    
    def do_OPTIONS(self):
        # Handle CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        return
