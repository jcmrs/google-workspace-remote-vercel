"""
Sample Endpoint Format Verification for Anthropic/Claude Custom Connector

This script outlines expected endpoint structures for OAuth, connect, configure, and manifest, based on public documentation and connector examples.

Use this as a checklist or basis for test coverage.
"""

EXPECTED_ENDPOINTS = [
    "/.well-known/anthropic-connector-manifest",
    "/connect",
    "/configure",
    "/oauth2/authorize",
    "/oauth2/token",
    "/oauth2/register",
    "/.well-known/oauth-protected-resource",
    "/.well-known/oauth-authorization-server",
    "/.well-known/oauth-client"
]

def check_endpoints(app):
    missing = []
    for endpoint in EXPECTED_ENDPOINTS:
        if not app.routes.get(endpoint):
            missing.append(endpoint)
    if missing:
        print("Missing endpoints:", missing)
    else:
        print("All expected endpoints are present.")

# Usage: Import your FastAPI/Flask/Django app and call check_endpoints(app)