"""
Project service - handles project creation and indexing
"""
import logging
from models.project import ProjectCreate, ProjectResponse
from datetime import datetime
from typing import List, Optional
import zipfile
import tempfile
import os
from pathlib import Path
from services.indexing_service import IndexingService
from config import BACKEND_DIR

logger = logging.getLogger(__name__)

# In-memory storage for MVP (will be replaced with SQLite later)
_projects_db = {}
_next_id = 1
_indexing_service = IndexingService()
PROJECTS_DATA_DIR = BACKEND_DIR / "data" / "projects"
PROJECTS_DATA_DIR.mkdir(parents=True, exist_ok=True)


class ProjectService:
    def create_project(self, project: ProjectCreate) -> ProjectResponse:
        """Create a new project"""
        global _next_id
        project_id = _next_id
        _next_id += 1
        
        # Create project directory
        project_dir = PROJECTS_DATA_DIR / str(project_id)
        project_dir.mkdir(parents=True, exist_ok=True)
        
        project_data = {
            "id": project_id,
            "name": project.name,
            "description": project.description,
            "created_at": datetime.now(),
            "file_count": 0,
            "project_path": str(project_dir),
        }
        _projects_db[project_id] = project_data
        return ProjectResponse(**project_data)
    
    def get_project(self, project_id: int) -> Optional[ProjectResponse]:
        """Get project by ID"""
        project_data = _projects_db.get(project_id)
        if project_data:
            return ProjectResponse(**project_data)
        return None
    
    def list_projects(self) -> List[ProjectResponse]:
        """List all projects"""
        return [ProjectResponse(**proj) for proj in _projects_db.values()]
    
    async def upload_and_index(self, project_id: int, file) -> dict:
        """Upload zip file, extract, and index the project"""
        if project_id not in _projects_db:
            raise ValueError(f"Project {project_id} not found")
        
        project_dir = Path(_projects_db[project_id]["project_path"])
        
        # Clear existing project files
        if project_dir.exists():
            import shutil
            shutil.rmtree(project_dir)
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Save uploaded zip file
        zip_path = project_dir / "project.zip"
        with open(zip_path, "wb") as f:
            content = file.file.read()
            f.write(content)
        
        # Extract zip to project directory
        extract_path = project_dir / "source"
        extract_path.mkdir(parents=True, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        
        # Index the project
        result = await _indexing_service.index_project(project_id, str(extract_path))
        
        # Update project file count
        _projects_db[project_id]["file_count"] = result.get("file_count", 0)
        
        return result
    
    async def list_files(self, project_id: int) -> List[str]:
        """List all files in a project"""
        if project_id not in _projects_db:
            raise ValueError(f"Project {project_id} not found")
        
        project_path = Path(_projects_db[project_id]["project_path"]) / "source"
        
        if not project_path.exists():
            return []
        
        files = []
        for root, dirs, filenames in os.walk(project_path):
            # Skip common ignore directories
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules', '.venv', '.pytest_cache'}]
            
            for filename in filenames:
                file_path = Path(root) / filename
                rel_path = os.path.relpath(file_path, project_path)
                files.append(rel_path.replace("\\", "/"))  # Normalize path separators
        
        return sorted(files)
    
    async def get_file_content(self, project_id: int, file_path: str) -> str:
        """Get the content of a file in a project"""
        if project_id not in _projects_db:
            raise ValueError(f"Project {project_id} not found")
        
        project_path = Path(_projects_db[project_id]["project_path"]) / "source"
        full_path = project_path / file_path
        
        # Security: ensure the file is within the project directory
        try:
            full_path.resolve().relative_to(project_path.resolve())
        except ValueError:
            raise ValueError(f"Invalid file path: {file_path}")
        
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(full_path, 'r', encoding='latin-1') as f:
                return f.read()

