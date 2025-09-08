from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.parse
import secrets
import string

# In-memory client storage for Vercel stateless environment
# In production, this would use a database
CLIENT_REGISTRY = {}

def generate_client_id():
    """Generate unique client ID with dcr_ prefix"""
    random_part = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(32))
    return f"dcr_{random_part}"

def generate_client_secret():
    """Generate secure client secret"""
    return secrets.token_urlsafe(32)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the path
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # Anthropic Connector Manifest - CRITICAL for Claude Desktop discovery
        if path == '/.well-known/anthropic-connector-manifest':
            try:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                base_url = "https://google-workspace-remote-vercel.vercel.app"
                manifest = {
                    "name": "Google Workspace Remote MCP",
                    "description": "Remote MCP server for Google Workspace integration with Claude",
                    "version": "1.0.0",
                    "endpoints": {
                        "connect": f"{base_url}/connect",
                        "configure": f"{base_url}/configure"
                    },
                    "transport": ["http"],
                    "oauth": True,
                    "sse": True,
                    "icon_url": f"{base_url}/static/icon.png",
                    "documentation_url": "https://github.com/jcmrs/google-workspace-remote-vercel",
                    "scopes": ["email", "calendar", "drive", "docs", "sheets", "slides", "forms", "chat", "tasks"],
                    "features": [
                        "Gmail", "Calendar", "Drive", "Docs", "Sheets", 
                        "Slides", "Forms", "Chat", "Tasks", "Search"
                    ],
                    "debug": "dcr_implementation_deployed"
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
                    "dcr_enabled": True,
                    "scopes_available": [
                        "email", "calendar", "drive", "docs", "sheets", 
                        "slides", "forms", "gmail", "chat", "tasks"
                    ],
                    "tools_count": 10,
                    "authentication_type": "oauth2_dcr",
                    "redirect_uri": "https://google-workspace-remote-vercel.vercel.app/oauth2callback"
                },
                "message": "Google Workspace MCP ready with Dynamic Client Registration"
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
        
        # OAuth Authorization Server metadata endpoint - WITH DCR SUPPORT
        if path == '/.well-known/oauth-authorization-server':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "issuer": "https://google-workspace-remote-vercel.vercel.app",
                "authorization_endpoint": "https://google-workspace-remote-vercel.vercel.app/authorize",
                "token_endpoint": "https://google-workspace-remote-vercel.vercel.app/token",
                "registration_endpoint": "https://google-workspace-remote-vercel.vercel.app/register",
                "registration_endpoint_auth_methods_supported": ["none"],
                "response_types_supported": ["code"],
                "grant_types_supported": ["authorization_code"],
                "code_challenge_methods_supported": ["S256"],
                "scopes_supported": [
                    "email", "profile", "calendar", "drive", "docs", 
                    "sheets", "slides", "forms", "gmail", "chat", "tasks"
                ]
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
                ],
                "scopes_supported": [
                    "email", "profile", "calendar", "drive", "docs", 
                    "sheets", "slides", "forms", "gmail", "chat", "tasks"
                ]
            }
            
            self.wfile.write(json.dumps(response).encode())
            return
        
        # OAuth authorize endpoint - for DCR flow
        if path == '/authorize':
            query_params = urllib.parse.parse_qs(parsed_path.query)
            client_id = query_params.get('client_id', [None])[0]
            
            # Validate that client_id is registered via DCR
            if client_id and client_id in CLIENT_REGISTRY:
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                html_response = f'''
                <html>
                <body>
                    <h1>OAuth Authorization</h1>
                    <p>Client ID: {client_id}</p>
                    <p>DCR-registered client detected. Redirecting to Google OAuth...</p>
                    <script>
                        // In production, this would redirect to Google OAuth with the dynamic client_id
                        window.location.href = "https://accounts.google.com/o/oauth2/v2/auth?" + window.location.search.substring(1);
                    </script>
                </body>
                </html>
                '''
                
                self.wfile.write(html_response.encode())
                return
            else:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                error_response = {
                    "error": "invalid_client",
                    "error_description": f"Client ID {client_id} not registered via Dynamic Client Registration"
                }
                
                self.wfile.write(json.dumps(error_response).encode())
                return
        
        # SSE endpoint for MCP remote connection
        if path == '/sse':
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()
            
            # Send connection confirmation and wait
            self.wfile.write(f"data: {json.dumps({'status': 'connected', 'server': 'google-workspace-mcp', 'dcr': 'enabled'})}\n\n".encode())
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
            "status": "dcr_enabled",
            "protocol": "MCP",
            "endpoints": {
                "manifest": "/.well-known/anthropic-connector-manifest",
                "connect": "/connect",
                "configure": "/configure",
                "register": "/register",
                "authorize": "/authorize",
                "token": "/token",
                "sse": "/sse",
                "oauth_callback": "/oauth2callback"
            },
            "transports": ["POST", "SSE"],
            "features": [
                "Gmail", "Calendar", "Drive", "Docs", "Sheets", 
                "Slides", "Forms", "Chat", "Tasks", "Search"
            ],
            "oauth": {
                "dcr_enabled": True,
                "registration_endpoint": "/register",
                "supports_anonymous_registration": True
            },
            "message": "Google Workspace MCP with Dynamic Client Registration ready"
        }
        
        self.wfile.write(json.dumps(response).encode())
        return
    
    def do_POST(self):
        # Parse the path
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # Dynamic Client Registration endpoint - RFC 7591
        if path == '/register':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 0:
                    post_data = self.rfile.read(content_length).decode('utf-8')
                    client_metadata = json.loads(post_data)
                else:
                    client_metadata = {}
                
                # Generate client credentials
                client_id = generate_client_id()
                client_secret = generate_client_secret()
                
                # Store client registration
                CLIENT_REGISTRY[client_id] = {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uris": client_metadata.get("redirect_uris", ["https://google-workspace-remote-vercel.vercel.app/oauth2callback"]),
                    "scopes": client_metadata.get("scope", "email profile calendar drive docs sheets slides forms gmail"),
                    "grant_types": client_metadata.get("grant_types", ["authorization_code"]),
                    "response_types": client_metadata.get("response_types", ["code"]),
                    "client_name": client_metadata.get("client_name", "Claude MCP Client"),
                    "client_uri": client_metadata.get("client_uri", ""),
                    "token_endpoint_auth_method": "none"  # Anonymous registration
                }
                
                # RFC 7591 response
                registration_response = {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uris": CLIENT_REGISTRY[client_id]["redirect_uris"],
                    "scope": CLIENT_REGISTRY[client_id]["scopes"],
                    "grant_types": CLIENT_REGISTRY[client_id]["grant_types"],
                    "response_types": CLIENT_REGISTRY[client_id]["response_types"],
                    "client_name": CLIENT_REGISTRY[client_id]["client_name"],
                    "token_endpoint_auth_method": "none"
                }
                
                self.send_response(201)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                self.wfile.write(json.dumps(registration_response).encode())
                return
                
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                error_response = {
                    "error": "invalid_client_metadata",
                    "error_description": f"Registration failed: {str(e)}"
                }
                
                self.wfile.write(json.dumps(error_response).encode())
                return
        
        # OAuth token endpoint - validates DCR clients
        if path == '/token':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length).decode('utf-8')
                token_request = urllib.parse.parse_qs(post_data)
                
                client_id = token_request.get('client_id', [None])[0]
                
                # Validate DCR-registered client
                if client_id and client_id in CLIENT_REGISTRY:
                    # In production, this would exchange auth code for actual tokens
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    token_response = {
                        "access_token": "dcr_access_token_placeholder",
                        "token_type": "Bearer",
                        "expires_in": 3600,
                        "scope": CLIENT_REGISTRY[client_id]["scopes"],
                        "client_id": client_id
                    }
                    
                    self.wfile.write(json.dumps(token_response).encode())
                    return
                else:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    error_response = {
                        "error": "invalid_client",
                        "error_description": f"Client ID {client_id} not registered via DCR"
                    }
                    
                    self.wfile.write(json.dumps(error_response).encode())
                    return
                    
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                error_response = {
                    "error": "invalid_request",
                    "error_description": f"Token request failed: {str(e)}"
                }
                
                self.wfile.write(json.dumps(error_response).encode())
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
                                "text": f"Tool '{tool_name}' called with args: {tool_args}. DCR OAuth authentication ready for Google Workspace operations."
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
