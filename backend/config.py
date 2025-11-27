"""
Configuration module - centralizes environment variables and settings
"""
import os
from pathlib import Path

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Embedding Configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# FAISS Data Directory
# Get the backend directory (parent of this config file)
BACKEND_DIR = Path(__file__).parent
FAISS_DATA_DIR = Path(os.getenv("FAISS_DATA_DIR", str(BACKEND_DIR / "data" / "faiss")))
FAISS_DATA_DIR.mkdir(parents=True, exist_ok=True)

