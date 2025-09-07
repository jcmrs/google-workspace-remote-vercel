from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World from FastAPI on Vercel!", "status": "working"}

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "google-workspace-remote-vercel"}

@app.get("/api/test")
def test_endpoint():
    return {"test": "success", "deployment": "vercel", "framework": "fastapi"}
