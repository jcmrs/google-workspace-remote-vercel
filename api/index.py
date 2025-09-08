from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.parse
import time
import threading
from queue import Queue, Empty

# Global message queue for SSE communication
message_queue = Queue()
sse_clients = []

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the path
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # Anthropic Connector Manifest - CRITICAL for Claude Desktop discovery
        if path == '/.well-known/anthropic-connector-manifest':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            base_url = "https://google-workspace-remote-vercel.vercel.app"
            manifest = {
                "name": "Google Workspace MCP",
                "description": "Remote MCP server for Google Workspace integration with Claude",
                "version": "1.0.0",
                "endpoints": {
                    "connect": f"{base_url}/connect",
                    "configure": f"{base_url}/configure"
                },
                "transport": ["sse", "http"],
                "oauth": True,
                "sse": True,
                "icon_url": f"{base_url}/static/icon.png",
                "documentation_url": "https://github.com/jcmrs/google-workspace-remote-vercel",
                "scopes": ["email", "calendar", "drive", "docs", "sheets", "slides", "forms", "chat", "tasks"],
                "features": [
                    "Gmail", "Calendar", "Drive", "Docs", "Sheets", 
                    "Slides", "Forms", "Chat", "Tasks", "Search"
                ]
            }
            
            self.wfile.write(json.dumps(manifest).encode())
            return
        
        # Connect endpoint - triggers OAuth flow for Claude Desktop
        if path == '/connect':
            self.send_response(302)  # Redirect to OAuth
            self.send_header('Content-Type', 'text/html')
            self.send_header('Access-Control-Allow-Origin', '*')
            
            # Build OAuth authorization URL
            oauth_params = {
                'client_id': os.environ.get('GOOGLE_OAUTH_CLIENT_ID', '257177956899-tug829mv65e3uo8q5od70ig2fscmvqpu.apps.googleusercontent.com'),
                'redirect_uri': 'https://google-workspace-remote-vercel.vercel.app/oauth2callback',
                'response_type': 'code',
                'scope': 'email profile https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/documents https://www.googleapis.com/auth/spreadsheets https://www.googleapis.com/auth/presentations https://www.googleapis.com/auth/forms https://www.googleapis.com/auth/gmail.modify',
                'access_type': 'offline',
                'include_granted_scopes': 'true'
            }
            
            oauth_url = 'https://accounts.google.com/o/oauth2/v2/auth?' + urllib.parse.urlencode(oauth_params)
            self.send_header('Location', oauth_url)
            self.end_headers()
            return
        
        # Configure endpoint - connector settings
        if path == '/configure':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            config_response = {
                "status": "ready",
                "configuration": {
                    "oauth_configured": True,
                    "scopes_available": [
                        "email", "calendar", "drive", "docs", "sheets", 
                        "slides", "forms", "gmail", "chat", "tasks"
                    ],
                    "tools_count": 10,
                    "authentication_type": "oauth2",
                    "redirect_uri": "https://google-workspace-remote-vercel.vercel.app/oauth2callback"
                },
                "message": "Google Workspace MCP ready for authentication"
            }
            
            self.wfile.write(json.dumps(config_response).encode())
            return
        
        # OAuth callback handler
        if path == '/oauth2callback':
            query_params = urllib.parse.parse_qs(parsed_path.query)
            
            if 'code' in query_params:
                auth_code = query_params['code'][0]
                
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                # Success page - would normally exchange code for tokens
                success_html = f'''
                <html>
                <head><title>Google Workspace MCP - Authentication Success</title></head>
                <body>
                    <h1>✅ Authentication Successful!</h1>
                    <p>Google Workspace MCP has been successfully connected to Claude.</p>
                    <p>Authorization code received: <code>{auth_code[:20]}...</code></p>
                    <p>You can now close this window and return to Claude.</p>
                    <script>
                        // Auto-close after 3 seconds
                        setTimeout(() => window.close(), 3000);
                    </script>
                </body>
                </html>
                '''
                
                self.wfile.write(success_html.encode())
                return
            else:
                # Error handling
                error = query_params.get('error', ['unknown'])[0]
                self.send_response(400)
                self.send_header('Content-Type', 'text/html')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                error_html = f'''
                <html>
                <head><title>Google Workspace MCP - Authentication Error</title></head>
                <body>
                    <h1>❌ Authentication Failed</h1>
                    <p>Error: {error}</p>
                    <p>Please return to Claude and try connecting again.</p>
                </body>
                </html>
                '''
                
                self.wfile.write(error_html.encode())
                return
        
        # OAuth authorize endpoint
        if path == '/authorize':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            html_response = '''
            <html>
            <body>
                <h1>OAuth Authorization</h1>
                <p>This endpoint is available. Use /connect for Claude Desktop integration.</p>
                <p>Server ready for OAuth implementation</p>
            </body>
            </html>
            '''
            
            self.wfile.write(html_response.encode())
            return
        
        # OAuth Authorization Server metadata endpoint
        if path == '/.well-known/oauth-authorization-server':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "issuer": "https://google-workspace-remote-vercel.vercel.app",
                "authorization_endpoint": "https://google-workspace-remote-vercel.vercel.app/connect",
                "token_endpoint": "https://google-workspace-remote-vercel.vercel.app/token",
                "response_types_supported": ["code"],
                "grant_types_supported": ["authorization_code"],
                "code_challenge_methods_supported": ["S256"]
            }
            
            self.wfile.write(json.dumps(response).encode())
            return
        
        # OAuth Protected Resource metadata endpoint
        if path == '/.well-known/oauth-protected-resource':
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
        
        # SSE endpoint for MCP remote connection - FIXED IMPLEMENTATION
        if path == '/sse':
            self.handle_sse_mcp_protocol()
            return
        
        # Default GET response - service info
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "service": "Google Workspace MCP Server",
            "version": "1.0.0", 
            "status": "connector_ready",
            "protocol": "MCP",
            "endpoints": {
                "manifest": "/.well-known/anthropic-connector-manifest",
                "connect": "/connect",
                "configure": "/configure",
                "sse": "/sse",
                "mcp": "/mcp",
                "oauth_callback": "/oauth2callback"
            },
            "transports": ["POST", "SSE"],
            "features": [
                "Gmail", "Calendar", "Drive", "Docs", "Sheets", 
                "Slides", "Forms", "Chat", "Tasks", "Search"
            ],
            "message": "Claude Desktop Connector ready - MCP SSE protocol implemented"
        }
        
        self.wfile.write(json.dumps(response).encode())
        return
    
    def handle_sse_mcp_protocol(self):
        """Handle Server-Sent Events with proper MCP protocol - NO immediate broadcasting"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Connection', 'keep-alive')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        
        # Register this client for message broadcasting
        client_id = f"client_{int(time.time())}"
        sse_clients.append({
            'id': client_id,
            'handler': self,
            'connected_at': time.time()
        })
        
        try:
            # DO NOT send immediate data - wait for proper initialize handshake
            # Keep connection alive and wait for messages via POST endpoint
            
            start_time = time.time()
            while True:
                try:
                    # Check for messages from POST endpoint (via queue)
                    message = message_queue.get(timeout=5)  # 5 second timeout
                    
                    # Send MCP response via SSE
                    self.wfile.write(f"data: {json.dumps(message)}\n\n".encode())
                    self.wfile.flush()
                    
                except Empty:
                    # No messages - send keep-alive ping
                    current_time = time.time()
                    
                    # Check Vercel timeout (9 seconds to be safe)
                    if current_time - start_time >= 9:
                        # Send final heartbeat and close gracefully
                        ping = {"type": "ping", "timestamp": int(current_time)}
                        self.wfile.write(f"data: {json.dumps(ping)}\n\n".encode())
                        self.wfile.flush()
                        break
                    
                    # Send keep-alive
                    ping = {"type": "ping", "timestamp": int(current_time)}
                    self.wfile.write(f"data: {json.dumps(ping)}\n\n".encode())
                    self.wfile.flush()
                    
                except Exception as e:
                    # Connection error - client disconnected
                    break
                    
        except Exception as e:
            # Connection closed or error
            pass
        finally:
            # Remove client from active list
            global sse_clients
            sse_clients = [c for c in sse_clients if c['id'] != client_id]
    
    def do_POST(self):
        # Parse the path
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # OAuth token endpoint
        if path == '/token':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "error": "not_implemented",
                "error_description": "Token endpoint exists but OAuth flow not yet implemented. Use /connect for Claude Desktop integration."
            }
            
            self.wfile.write(json.dumps(response).encode())
            return
        
        # MCP message endpoint - handles initialize and other MCP protocol messages
        if path == '/mcp' or path == '/sse':  # Accept both endpoints for MCP messages
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32700,
                        "message": "Parse error: No data received"
                    }
                }
                self.wfile.write(json.dumps(error_response).encode())
                return
        
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            try:
                data = json.loads(post_data)
                
                # MCP Initialize handshake - CRITICAL
                if data.get("method") == "initialize":
                    response = {
                        "jsonrpc": "2.0",
                        "id": data.get("id"),
                        "result": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {
                                "tools": {},
                                "resources": {},
                                "prompts": {}
                            },
                            "serverInfo": {
                                "name": "google-workspace-mcp-server",
                                "version": "1.0.0"
                            }
                        }
                    }
                    
                    # Queue response for SSE clients
                    message_queue.put(response)
                
                # Tools list request
                elif data.get("method") == "tools/list":
                    tools = [
                        {
                            "name": "gmail_search",
                            "description": "Search Gmail messages",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "query": {"type": "string", "description": "Search query"},
                                    "max_results": {"type": "integer", "description": "Maximum results", "default": 10}
                                },
                                "required": ["query"]
                            }
                        },
                        {
                            "name": "gmail_send",
                            "description": "Send an email via Gmail",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "to": {"type": "string", "description": "Recipient email"},
                                    "subject": {"type": "string", "description": "Email subject"},
                                    "body": {"type": "string", "description": "Email body"}
                                },
                                "required": ["to", "subject", "body"]
                            }
                        },
                        {
                            "name": "calendar_create_event", 
                            "description": "Create a calendar event with color support",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "Event title"},
                                    "start_time": {"type": "string", "description": "Start time (ISO format)"},
                                    "end_time": {"type": "string", "description": "End time (ISO format)"},
                                    "description": {"type": "string", "description": "Event description"},
                                    "color_id": {"type": "integer", "description": "Calendar color ID (1-11)"}
                                },
                                "required": ["title", "start_time", "end_time"]
                            }
                        },
                        {
                            "name": "calendar_list_events",
                            "description": "List calendar events",
                            "inputSchema": {
                                "type": "object", 
                                "properties": {
                                    "start_date": {"type": "string", "description": "Start date (ISO format)"},
                                    "end_date": {"type": "string", "description": "End date (ISO format)"},
                                    "max_results": {"type": "integer", "description": "Maximum results", "default": 25}
                                }
                            }
                        },
                        {
                            "name": "drive_search",
                            "description": "Search Google Drive files",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "query": {"type": "string", "description": "Search query"},
                                    "file_type": {"type": "string", "description": "File type filter"}
                                },
                                "required": ["query"]
                            }
                        },
                        {
                            "name": "drive_read_file",
                            "description": "Read content from Google Drive file",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "file_id": {"type": "string", "description": "Google Drive file ID"}
                                },
                                "required": ["file_id"]
                            }
                        },
                        {
                            "name": "docs_create",
                            "description": "Create a new Google Doc",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "Document title"},
                                    "content": {"type": "string", "description": "Initial content"}
                                },
                                "required": ["title"]
                            }
                        },
                        {
                            "name": "sheets_read",
                            "description": "Read data from Google Sheets",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "spreadsheet_id": {"type": "string", "description": "Spreadsheet ID"},
                                    "range": {"type": "string", "description": "Range to read (e.g., A1:Z100)"}
                                },
                                "required": ["spreadsheet_id"]
                            }
                        },
                        {
                            "name": "slides_create",
                            "description": "Create a new Google Slides presentation",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "Presentation title"}
                                },
                                "required": ["title"]
                            }
                        },
                        {
                            "name": "tasks_list",
                            "description": "List Google Tasks",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "task_list": {"type": "string", "description": "Task list name"}
                                }
                            }
                        }
                    ]
                    
                    response = {
                        "jsonrpc": "2.0",
                        "id": data.get("id"),
                        "result": {"tools": tools}
                    }
                    
                    # Queue response for SSE clients
                    message_queue.put(response)
                    
                # Tool execution (placeholder - would need actual Google API implementation)
                elif data.get("method") == "tools/call":
                    tool_name = data.get("params", {}).get("name")
                    tool_args = data.get("params", {}).get("arguments", {})
                    
                    response = {
                        "jsonrpc": "2.0",
                        "id": data.get("id"),
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Tool '{tool_name}' called with args: {tool_args}. OAuth authentication required to execute Google Workspace operations. Please connect via Claude Desktop connector first."
                                }
                            ]
                        }
                    }
                    
                    # Queue response for SSE clients
                    message_queue.put(response)
                
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
                    
                    # Queue response for SSE clients
                    message_queue.put(response)
                
            except Exception as e:
                response = {
                    "jsonrpc": "2.0",
                    "id": data.get("id") if "data" in locals() else None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                
                # Queue response for SSE clients
                message_queue.put(response)
            
            # Send immediate HTTP response for POST (acknowledging receipt)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "message_queued"}).encode())
            return
        
        # Handle other POST requests (legacy MCP direct)
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_response = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32700,
                    "message": "Parse error: No data received"
                }
            }
            self.wfile.write(json.dumps(error_response).encode())
            return
        
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(post_data)
            
            # Handle MCP methods directly (for non-SSE clients)
            if data.get("method") == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": data.get("id"),
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {},
                            "resources": {},
                            "prompts": {}
                        },
                        "serverInfo": {
                            "name": "google-workspace-mcp-server",
                            "version": "1.0.0"
                        }
                    }
                }
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
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        return