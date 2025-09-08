# External MCP Custom Connector Example Projects & Analysis

_Last updated: 2025-09-07_

---

## Overview

This doc provides references to external repositories and resources useful for studying Claude-compatible remote MCP servers, especially those supporting seamless authentication and integration with Claude Desktop, web, and mobile apps.  
It also logs technical analysis of endpoint and authentication flows, and highlights format/extraction considerations for Claude vs Copilot assisted development.

---

## Key Example Repos & Resources

### 1. **nganiet/mcp-vercel**  
- **Repo:** [https://github.com/nganiet/mcp-vercel](https://github.com/nganiet/mcp-vercel)  
- **Focus:** MCP server for Claude using Vercel authentication, remote server architecture, custom connector manifest/endpoint implementation.
- **Why Relevant:** Demonstrates remote server setup, external OAuth provider integration, and likely correct manifest and Connect button flows for Claude Desktop.

### 2. **jcmrs/claude-github-mcp-server-integration**  
- **Repo:** [https://github.com/jcmrs/claude-github-mcp-server-integration](https://github.com/jcmrs/claude-github-mcp-server-integration)  
- **Focus:** Local MCP server for GitHub, with authentication and connector logic.
- **Why Relevant:** Use for cross-reference, especially for endpoints and manifest structure.

### 3. **Documentation & Tutorials**
- ["Getting Started with Custom Connectors Using Remote MCP"](https://support.anthropic.com/en/articles/11175166-getting-started-with-custom-connectors-using-remote-mcp)
- ["How to Install Claude Custom Connectors - Remote MCP"](https://www.remote-mcp.com/claude-integrations)
- ["How to set up Github MCP server for use with Claude Desktop on Windows and Mac"](https://allthings.how/how-to-set-up-github-mcp-server-for-use-with-claude-desktop-on-windows-and-mac/)
- ["Using Claude Desktop with MCP GitHub Server - amiable.dev"](https://amiable.dev/using-claude-with-mcp/)

---

## Technical Analysis: Endpoints, Authentication Flows, and Manifest

### **A. Endpoint Structure**

- **Essential endpoints for Claude Custom Connector:**
  - `/.well-known/anthropic-connector-manifest` (Connector manifest)
  - `/connect` (Connector handshake, triggers OAuth or similar flows)
  - `/configure` (Settings/config endpoint)
  - `/oauth2/authorize`, `/oauth2/token`, `/oauth2/register` (OAuth flows)
  - `/.well-known/oauth-protected-resource`
  - `/.well-known/oauth-authorization-server`
  - `/.well-known/oauth-client`

- **Manifest Endpoint Example (from mcp-vercel):**
  ```json
  {
    "name": "Vercel MCP",
    "description": "Connect Claude to your Vercel account",
    "endpoints": {
      "connect": "https://mcp-vercel.vercel.app/connect",
      "configure": "https://mcp-vercel.vercel.app/configure"
    },
    "transport": ["sse", "http"],
    "oauth": true,
    "sse": true,
    "icon_url": "https://mcp-vercel.vercel.app/static/icon.png",
    "documentation_url": "https://github.com/nganiet/mcp-vercel",
    "version": "1.0.0"
  }
  ```
  _Adjust endpoints for your own deployment URLs._

### **B. Authentication Flow**

- **Vercel MCP Example:**
  - User clicks "Connect" in Claude Desktop.
  - Connector manifest triggers handshake at `/connect`, which redirects to Vercel OAuth page.
  - Upon successful authentication, OAuth callback is handled by MCP server, which then exposes tokens and user info for Claude tool calls.
  - Claude Desktop, web, and mobile clients can then use MCP tools via authenticated session.

- **Differences vs Local MCP:**
  - _Remote MCP must handle CORS, public endpoint exposure, and full OAuth handshake._
  - _Local MCP may use non-standard transports or direct stdio, but requires different endpoint logic and limited external authentication._

### **C. Format & Extraction Considerations**

- **For Claude-assisted development:**  
  Claude and Copilot can process code, configs, and manifests in standard formats (JSON, YAML, Python, etc).  
  - **Preferred extraction method:**  
    - Use raw code/config files from example repos (manifest.json, Python/JS endpoints).
    - Reference endpoint shapes and OAuth flow logic as code snippets or config blocks.
    - Avoid binary blobs or undocumented formats.

- **For analysis:**  
  - Review endpoint paths, manifest structure, and OAuth callback logic.
  - Compare with your repo’s implementation for gaps or deviations.

---

## Recommendations

- Use [nganiet/mcp-vercel](https://github.com/nganiet/mcp-vercel) as primary technical reference for remote MCP + custom connector integration.
- Extract manifest, endpoint, and OAuth logic as code/config blocks for Claude/Copilot-assisted workflow.
- Cross-reference with your own local MCP repo for architecture differences.
- Regularly review external docs and public repo updates for new requirements or bug fixes.

---

## Protocol Log

- **2025-09-07:** Initial references and technical analysis added for MCP custom connector onboarding and investigation.
- **Role:** Autonomous Project Owner → Lead Developer → Documentation Specialist.