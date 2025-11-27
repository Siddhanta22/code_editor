"""
IntelliForge Backend - FastAPI Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import projects, chat, explain, usage, impact, files

app = FastAPI(title="IntelliForge API", version="0.1.0")

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(projects.router, prefix="/api", tags=["projects"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(explain.router, prefix="/api", tags=["explain"])
app.include_router(usage.router, prefix="/api", tags=["usage"])
app.include_router(impact.router, prefix="/api", tags=["impact"])
app.include_router(files.router, prefix="/api", tags=["files"])


@app.get("/")
def root():
    return {"message": "IntelliForge API", "status": "running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

