# IntelliForge

AI-powered, project-aware code editor with architecture understanding and RAG capabilities.

## Architecture

- **Backend**: FastAPI with AST parsing, symbol extraction, and embeddings (FAISS)
- **Frontend**: React + Vite with Monaco Editor

## Quick Start

### Backend

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Backend runs on http://localhost:8000

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on http://localhost:5173

## Features

- ✅ Project creation and file upload
- ✅ AST parsing for Python (JavaScript coming soon)
- ✅ Symbol extraction (functions, classes, methods)
- ✅ Project-aware chat (stub - LLM integration pending)
- ✅ Code explanation (stub - LLM integration pending)
- ⏳ FAISS embeddings (stub - implementation pending)
- ⏳ Usage/call analysis
- ⏳ Impact analysis

## Next Steps

1. Integrate LLM API (OpenAI/Anthropic) for chat and explain
2. Implement FAISS embeddings with sentence-transformers
3. Build import/call graph
4. Add usage analysis endpoint
5. Add impact analysis

