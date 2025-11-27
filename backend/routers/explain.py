"""
Explain router - handles code explanation requests
"""
import logging
from fastapi import APIRouter, HTTPException
from models.explain import ExplainRequest, ExplainResponse
from services.explain_service import ExplainService

logger = logging.getLogger(__name__)

router = APIRouter()
explain_service = ExplainService()


@router.post("/projects/{project_id}/explain", response_model=ExplainResponse)
async def explain_code(project_id: int, request: ExplainRequest):
    """Explain selected code with project context"""
    if not request.code or not request.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")
    
    try:
        return await explain_service.explain_code(project_id, request)
    except HTTPException:
        # Re-raise HTTP exceptions (from LLM service, etc.)
        raise
    except ValueError as e:
        logger.error(f"Validation error explaining code for project {project_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error explaining code for project {project_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error explaining code: {str(e)}")


@router.post("/explain", response_model=ExplainResponse)
async def explain_code_standalone(request: ExplainRequest):
    """Explain code without project context"""
    if not request.code or not request.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")
    
    try:
        return await explain_service.explain_code_standalone(request)
    except HTTPException:
        # Re-raise HTTP exceptions (from LLM service, etc.)
        raise
    except ValueError as e:
        logger.error(f"Validation error explaining code: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error explaining code: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error explaining code: {str(e)}")

