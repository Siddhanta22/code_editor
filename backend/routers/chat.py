"""
Chat router - handles project-aware chat queries
"""
import logging
from fastapi import APIRouter, HTTPException
from models.chat import ChatRequest, ChatResponse
from services.chat_service import ChatService

logger = logging.getLogger(__name__)

router = APIRouter()
chat_service = ChatService()


@router.post("/projects/{project_id}/chat", response_model=ChatResponse)
async def chat_with_project(project_id: int, request: ChatRequest):
    """Chat with AI about the project"""
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    try:
        return await chat_service.process_chat(project_id, request)
    except HTTPException:
        # Re-raise HTTP exceptions (from LLM service, etc.)
        raise
    except ValueError as e:
        logger.error(f"Validation error in chat for project {project_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in chat for project {project_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")

