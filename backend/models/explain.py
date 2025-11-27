"""
Explain models
"""
from pydantic import BaseModel
from typing import Optional


class ExplainRequest(BaseModel):
    code: str
    file_path: Optional[str] = None
    language: Optional[str] = None  # "python", "javascript", etc.
    project_id: Optional[int] = None  # Optional project ID for context-aware explanation


class ExplainResponse(BaseModel):
    explanation: str
    complexity: Optional[str] = None
    issues: Optional[List[str]] = []

