"""
Files router - handles file listing and content retrieval
"""
import logging
from fastapi import APIRouter, HTTPException, Query
from services.project_service import ProjectService

logger = logging.getLogger(__name__)

router = APIRouter()
project_service = ProjectService()


@router.get("/projects/{project_id}/files")
async def list_project_files(project_id: int):
    """List all files in a project"""
    try:
        files = await project_service.list_files(project_id)
        return files
    except ValueError as e:
        logger.error(f"Project not found for file listing: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error listing files for project {project_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")


@router.get("/projects/{project_id}/file")
async def get_project_file(
    project_id: int,
    file_path: str = Query(..., description="Relative file path within the project")
):
    """Get the content of a file in a project"""
    if not file_path or not file_path.strip():
        raise HTTPException(status_code=400, detail="file_path cannot be empty")
    
    try:
        content = await project_service.get_file_content(project_id, file_path.strip())
        return {
            "file_path": file_path,
            "content": content
        }
    except FileNotFoundError as e:
        logger.error(f"File not found for project {project_id}: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        logger.error(f"Invalid file path for project {project_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error getting file content for project {project_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting file content: {str(e)}")

