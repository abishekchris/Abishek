from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import router


# ---------------------------------------------------------
# Create FastAPI application
# ---------------------------------------------------------

app = FastAPI(
    title="LegalEase API",
    version="1.0.0",
    description="AI-powered legal document generation API.",
)


# ---------------------------------------------------------
# CORS configuration
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Include API routes
# ---------------------------------------------------------

app.include_router(router)


# ---------------------------------------------------------
# Root endpoint
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "application": "LegalEase",
        "status": "running"
    }


# ---------------------------------------------------------
# Health-check endpoint
# ---------------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }