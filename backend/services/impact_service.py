"""
Impact Service - analyzes potential impact of changing a symbol using call graph
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Set, Any

from fastapi import HTTPException

from config import BACKEND_DIR
from services.llm_service import generate_response

logger = logging.getLogger(__name__)

GRAPH_DATA_DIR = BACKEND_DIR / "data" / "graph"
GRAPH_DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load_graph(project_id: str) -> Dict[str, Any]:
    """Load call graph for a project"""
    graph_path = GRAPH_DATA_DIR / f"{project_id}.json"
    
    if not graph_path.exists():
        logger.debug(f"Graph file not found for project {project_id}")
        raise FileNotFoundError(f"Call graph not found for project {project_id}. Please index the project first.")
    
    try:
        with open(graph_path, "r") as f:
            graph_data = json.load(f)
        return graph_data
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing graph JSON for project {project_id}: {str(e)}")
        raise ValueError(f"Invalid graph data for project {project_id}")
    except Exception as e:
        logger.error(f"Error loading graph for project {project_id}: {str(e)}")
        raise


def _find_symbol(symbols: List[Dict], symbol_name: str, file_path: str) -> Dict:
    """Find a symbol by name and file_path"""
    for symbol in symbols:
        if symbol.get("name") == symbol_name and symbol.get("file_path") == file_path:
            return symbol
    raise ValueError(f"Symbol '{symbol_name}' not found in file '{file_path}'")


def _get_transitive_callers(edges: List[Dict], target_id: int) -> Set[int]:
    """
    Get all symbols that call the target symbol (transitive closure)
    
    Args:
        edges: List of edges in the call graph
        target_id: ID of the target symbol
    
    Returns:
        Set of symbol IDs that call the target (directly or indirectly)
    """
    callers = set()
    to_visit = {target_id}
    
    # Build reverse adjacency list (who calls whom)
    reverse_edges: Dict[int, List[int]] = {}
    for edge in edges:
        from_id = edge["from"]
        to_id = edge["to"]
        if to_id not in reverse_edges:
            reverse_edges[to_id] = []
        reverse_edges[to_id].append(from_id)
    
    # BFS to find all transitive callers
    visited = set()
    while to_visit:
        current = to_visit.pop()
        if current in visited:
            continue
        visited.add(current)
        
        # Add direct callers
        if current in reverse_edges:
            for caller_id in reverse_edges[current]:
                if caller_id not in visited:
                    callers.add(caller_id)
                    to_visit.add(caller_id)
    
    return callers


async def analyze_impact(
    project_id: str,
    symbol_name: str,
    file_path: str,
    change_description: str = ""
) -> Dict[str, Any]:
    """
    Analyze the potential impact of changing a symbol
    
    Args:
        project_id: Project identifier
        symbol_name: Name of the symbol to analyze
        file_path: Relative file path where the symbol is defined
        change_description: Optional description of the proposed change
    
    Returns:
        Dictionary with impact analysis including affected symbols and AI-generated analysis
    
    Raises:
        FileNotFoundError: If graph file doesn't exist
        ValueError: If symbol not found
    """
    # Load call graph
    graph_data = _load_graph(project_id)
    symbols = graph_data.get("symbols", [])
    edges = graph_data.get("edges", [])
    
    # Find target symbol
    target_symbol = _find_symbol(symbols, symbol_name, file_path)
    target_id = target_symbol["id"]
    
    # Find all symbols that call this one (transitive closure)
    affected_symbol_ids = _get_transitive_callers(edges, target_id)
    
    # Get details of affected symbols
    affected_symbols = [s for s in symbols if s.get("id") in affected_symbol_ids]
    
    # Also get what this symbol calls (dependencies)
    dependencies = [edge["to"] for edge in edges if edge["from"] == target_id]
    dependency_symbols = [s for s in symbols if s.get("id") in dependencies]
    
    # Build context for LLM
    context = _build_impact_context(
        target_symbol,
        affected_symbols,
        dependency_symbols,
        change_description
    )
    
    # Generate impact analysis using LLM
    system_prompt = (
        "You are a code architecture analyst. Analyze the potential impact of changing a code symbol. "
        "Consider breaking changes, compatibility issues, test requirements, and refactoring needs. "
        "Be concise but thorough. Structure your response with clear sections."
    )
    
    user_prompt = context
    
    try:
        analysis = await generate_response(system_prompt, user_prompt)
    except HTTPException:
        # Re-raise HTTP exceptions from LLM service
        raise
    except Exception as e:
        logger.error(f"Error generating impact analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating impact analysis: {str(e)}"
        )
    
    return {
        "symbol": target_symbol,
        "affected_symbols": affected_symbols,
        "affected_count": len(affected_symbols),
        "dependencies": dependency_symbols,
        "dependency_count": len(dependency_symbols),
        "analysis": analysis,
        "risk_level": _assess_risk_level(len(affected_symbols), len(dependency_symbols))
    }


def _build_impact_context(
    target_symbol: Dict,
    affected_symbols: List[Dict],
    dependencies: List[Dict],
    change_description: str
) -> str:
    """Build context string for LLM impact analysis"""
    context = f"Analyze the impact of changing the following symbol:\n\n"
    context += f"Symbol: {target_symbol.get('name')}\n"
    context += f"Type: {target_symbol.get('type')}\n"
    context += f"File: {target_symbol.get('file_path')}\n\n"
    
    if change_description:
        context += f"Proposed change: {change_description}\n\n"
    
    context += f"Direct dependencies (symbols this calls): {len(dependencies)}\n"
    if dependencies:
        context += "Dependencies:\n"
        for dep in dependencies[:10]:  # Limit to first 10
            context += f"  - {dep.get('name')} ({dep.get('file_path')})\n"
        if len(dependencies) > 10:
            context += f"  ... and {len(dependencies) - 10} more\n"
    
    context += f"\nAffected code (symbols that call this, directly or transitively): {len(affected_symbols)}\n"
    if affected_symbols:
        context += "Affected symbols:\n"
        for sym in affected_symbols[:15]:  # Limit to first 15
            context += f"  - {sym.get('name')} ({sym.get('type')}) in {sym.get('file_path')}\n"
        if len(affected_symbols) > 15:
            context += f"  ... and {len(affected_symbols) - 15} more\n"
    
    context += "\nProvide an analysis of:\n"
    context += "1. Potential breaking changes\n"
    context += "2. Test coverage needs\n"
    context += "3. Refactoring recommendations\n"
    context += "4. Risk assessment"
    
    return context


def _assess_risk_level(affected_count: int, dependency_count: int) -> str:
    """Assess risk level based on impact metrics"""
    total_impact = affected_count + dependency_count
    
    if total_impact == 0:
        return "low"
    elif total_impact < 5:
        return "low"
    elif total_impact < 15:
        return "medium"
    else:
        return "high"

