"""
Impact analysis models
"""
from pydantic import BaseModel
from typing import Optional


class ImpactRequest(BaseModel):
    symbol_name: str
    file_path: str
    change_description: Optional[str] = None


class ImpactResponse(BaseModel):
    symbol: dict
    affected_symbols: list
    affected_count: int
    dependencies: list
    dependency_count: int
    analysis: str
    risk_level: str

