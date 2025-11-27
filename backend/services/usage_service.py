"""
Usage Service - handles call graph queries for symbol usage
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from config import BACKEND_DIR

logger = logging.getLogger(__name__)

GRAPH_DATA_DIR = BACKEND_DIR / "data" / "graph"
GRAPH_DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_usage(project_id: str, symbol_name: str, file_path: str) -> Dict:
    """
    Get usage information for a symbol (what it calls and what calls it)
    
    Args:
        project_id: Project identifier
        symbol_name: Name of the symbol (function/method name)
        file_path: Relative file path where the symbol is defined
    
    Returns:
        Dictionary with symbol, calls (outgoing edges), and called_by (incoming edges)
    
    Raises:
        FileNotFoundError: If graph file doesn't exist
        ValueError: If symbol not found
    """
    graph_path = GRAPH_DATA_DIR / f"{project_id}.json"
    
    # Handle missing graph file gracefully
    if not graph_path.exists():
        logger.debug(f"Graph file not found for project {project_id}")
        raise FileNotFoundError(f"Call graph not found for project {project_id}. Please index the project first.")
    
    try:
        with open(graph_path, "r") as f:
            graph_data = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing graph JSON for project {project_id}: {str(e)}")
        raise ValueError(f"Invalid graph data for project {project_id}")
    except Exception as e:
        logger.error(f"Error loading graph for project {project_id}: {str(e)}")
        raise
    
    symbols = graph_data.get("symbols", [])
    edges = graph_data.get("edges", [])
    
    # Find the symbol by name and file_path
    symbol = None
    symbol_id = None
    
    for s in symbols:
        if s.get("name") == symbol_name and s.get("file_path") == file_path:
            symbol = s
            symbol_id = s.get("id")
            break
    
    if symbol is None:
        logger.debug(f"Symbol '{symbol_name}' not found in file '{file_path}' for project {project_id}")
        raise ValueError(f"Symbol '{symbol_name}' not found in file '{file_path}'")
    
    # Find what this symbol calls (outgoing edges)
    calls_symbol_ids = [edge["to"] for edge in edges if edge["from"] == symbol_id]
    calls = [s for s in symbols if s.get("id") in calls_symbol_ids]
    
    # Find what calls this symbol (incoming edges)
    called_by_symbol_ids = [edge["from"] for edge in edges if edge["to"] == symbol_id]
    called_by = [s for s in symbols if s.get("id") in called_by_symbol_ids]
    
    return {
        "symbol": symbol,
        "calls": calls,
        "called_by": called_by
    }

