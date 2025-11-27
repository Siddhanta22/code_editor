"""
Projects router - handles project creation and file uploads
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
from models.project import ProjectCreate, ProjectResponse
from services.project_service import ProjectService

router = APIRouter()
project_service = ProjectService()


@router.post("/projects", response_model=ProjectResponse)
def create_project(project: ProjectCreate):
    """Create a new project"""
    try:
        return project_service.create_project(project)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int):
    """Get project details"""
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("/projects", response_model=List[ProjectResponse])
def list_projects():
    """List all projects"""
    return project_service.list_projects()


@router.post("/projects/{project_id}/upload")
async def upload_project(project_id: int, file: UploadFile = File(...)):
    """Upload and index a project (zip file)"""
    if not file.filename or not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Only ZIP files are supported")
    
    try:
        result = await project_service.upload_and_index(project_id, file)
        return {"message": "Project uploaded and indexed", "details": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error indexing project: {str(e)}")

