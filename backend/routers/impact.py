"""
Impact router - handles impact analysis requests
"""
import logging
from fastapi import APIRouter, HTTPException
from models.impact import ImpactRequest, ImpactResponse
from services.impact_service import analyze_impact

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/projects/{project_id}/impact", response_model=ImpactResponse)
async def analyze_symbol_impact(project_id: int, request: ImpactRequest):
    """Analyze the potential impact of changing a symbol"""
    if not request.symbol_name or not request.symbol_name.strip():
        raise HTTPException(status_code=400, detail="symbol_name cannot be empty")
    
    if not request.file_path or not request.file_path.strip():
        raise HTTPException(status_code=400, detail="file_path cannot be empty")
    
    try:
        result = await analyze_impact(
            str(project_id),
            request.symbol_name.strip(),
            request.file_path.strip(),
            request.change_description or ""
        )
        return ImpactResponse(**result)
    except FileNotFoundError as e:
        logger.error(f"Graph not found for project {project_id}: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        logger.error(f"Symbol not found or invalid graph for project {project_id}: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        # Re-raise HTTP exceptions (from LLM service, etc.)
        raise
    except Exception as e:
        logger.error(f"Unexpected error analyzing impact for project {project_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error analyzing impact: {str(e)}")

