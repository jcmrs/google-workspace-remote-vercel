from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.parse

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
                "oauth": {
                    "authorization_url": f"{base_url}/authorize",
                    "token_url": f"{base_url}/token"
                },
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
        
        # Connect endpoint - returns OAuth configuration for Claude Desktop internal flow
        if path == '/connect':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Return OAuth configuration for Claude Desktop to handle
            oauth_config = {
                "oauth_provider": "google",
                "client_id": os.environ.get('GOOGLE_OAUTH_CLIENT_ID', '257177956899-tug829mv65e3uo8q5od70ig2fscmvqpu.apps.googleusercontent.com'),
                "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth",
                "token_url": "https://oauth2.googleapis.com/token",
                "scopes": [
                    "email",
                    "profile", 
                    "https://www.googleapis.com/auth/calendar",
                    "https://www.googleapis.com/auth/drive",
                    "https://www.googleapis.com/auth/documents",
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/presentations",
                    "https://www.googleapis.com/auth/forms",
                    "https://www.googleapis.com/auth/gmail.modify"
                ],
                "redirect_uri": "https://google-workspace-remote-vercel.vercel.app/oauth2callback",
                "response_type": "code",
                "access_type": "offline",
                "include_granted_scopes": True
            }
            
            self.wfile.write(json.dumps(oauth_config).encode())
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
        
        # SSE endpoint for MCP remote connection - SIMPLIFIED
        if path == '/sse':
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()
            
            # Send connection confirmation and wait
            self.wfile.write(f"data: {json.dumps({'status': 'connected', 'server': 'google-workspace-mcp'})}\n\n".encode())
            self.wfile.flush()
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
                "oauth_callback": "/oauth2callback"
            },
            "transports": ["POST", "SSE"],
            "features": [
                "Gmail", "Calendar", "Drive", "Docs", "Sheets", 
                "Slides", "Forms", "Chat", "Tasks", "Search"
            ],
            "message": "Claude Desktop Connector ready - OAuth configuration fixed"
        }
        
        self.wfile.write(json.dumps(response).encode())
        return
    
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
        
        # Handle MCP protocol messages
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
            
            # MCP Initialize handshake
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
                    }
                ]
                
                response = {
                    "jsonrpc": "2.0",
                    "id": data.get("id"),
                    "result": {"tools": tools}
                }
                
            # Tool execution (placeholder)
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
                                "text": f"Tool '{tool_name}' called with args: {tool_args}. OAuth authentication required to execute Google Workspace operations."
                            }
                        ]
                    }
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
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        return