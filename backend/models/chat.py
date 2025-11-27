"""
Chat models
"""
from pydantic import BaseModel
from typing import List, Optional


class ChatRequest(BaseModel):
    message: str
    context: Optional[List[str]] = None  # Optional file paths for context


class Reference(BaseModel):
    file_path: str
    line_start: int
    line_end: int
    snippet: str


class ChatResponse(BaseModel):
    answer: str
    references: List[Reference] = []

