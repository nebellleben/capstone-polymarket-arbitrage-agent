"""Minimal FastAPI app for testing Railway deployment."""

from fastapi import FastAPI
from datetime import datetime

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello from Railway", "timestamp": datetime.utcnow().isoformat()}

@app.get("/api/health")
async def health():
    return {"status": "healthy"}
