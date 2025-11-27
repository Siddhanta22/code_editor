"""
Project models (Pydantic schemas + DB models)
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    file_count: Optional[int] = 0

    class Config:
        from_attributes = True

