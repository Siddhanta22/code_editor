"""
Usage router - handles symbol usage and call graph queries
"""
import logging
from fastapi import APIRouter, HTTPException, Query
from services.usage_service import get_usage

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/projects/{project_id}/usage")
async def get_symbol_usage(
    project_id: int,
    symbol_name: str = Query(..., description="Name of the symbol (function/method)"),
    file_path: str = Query(..., description="Relative file path where the symbol is defined")
):
    """Get usage information for a symbol (what it calls and what calls it)"""
    if not symbol_name or not symbol_name.strip():
        raise HTTPException(status_code=400, detail="symbol_name cannot be empty")
    
    if not file_path or not file_path.strip():
        raise HTTPException(status_code=400, detail="file_path cannot be empty")
    
    try:
        result = get_usage(str(project_id), symbol_name.strip(), file_path.strip())
        return result
    except FileNotFoundError as e:
        logger.error(f"Graph not found for project {project_id}: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        logger.error(f"Symbol not found or invalid graph for project {project_id}: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error getting usage for project {project_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting symbol usage: {str(e)}")

