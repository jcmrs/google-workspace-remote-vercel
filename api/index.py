"""
Minimal FastAPI app for testing Vercel deployment
"""
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from Vercel!", "status": "working"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "minimal-test"}

# Export for Vercel
handler = app
