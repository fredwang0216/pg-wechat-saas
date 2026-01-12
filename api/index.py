from fastapi import FastAPI

app = FastAPI()

@app.get("/api/health")
def health():
    return {"status": "ok", "msg": "Minimal build"}

@app.get("/api/generate")
def generate():
    return {"status": "error", "msg": "Placeholder for dependency check"}
