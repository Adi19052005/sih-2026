
from fastapi import FastAPI

app = FastAPI(
    title="Sovereign AI Workbench",
    description="Local, air-gapped AI Workbench backend",
    version="0.1.0"
)


@app.get("/")
def root():
    """
    Root endpoint to verify the backend is running.
    """
    return {
        "message": "Sovereign AI Workbench is running locally",
        "mode": "air-gapped"
    }


@app.get("/health")
def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "service": "Sovereign AI Workbench Backend"
    }

