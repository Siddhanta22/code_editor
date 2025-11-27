"""
Embedding Service - handles embeddings generation and FAISS index management
"""
import asyncio
import json
import logging
import numpy as np
import faiss
from pathlib import Path
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL, FAISS_DATA_DIR

logger = logging.getLogger(__name__)

# Model will be loaded once at startup
_model: Optional[SentenceTransformer] = None

# Per-project locks for FAISS index and metadata writes
_locks: Dict[str, asyncio.Lock] = {}
_locks_lock = asyncio.Lock()


async def _get_lock(project_id: str) -> asyncio.Lock:
    """Get or create an asyncio.Lock for a project (thread-safe)"""
    async with _locks_lock:
        if project_id not in _locks:
            _locks[project_id] = asyncio.Lock()
        return _locks[project_id]


def _get_model() -> SentenceTransformer:
    """Load and return the sentence transformer model (singleton)"""
    global _model
    if _model is None:
        logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
        _model = SentenceTransformer(EMBEDDING_MODEL)
        logger.info("Embedding model loaded successfully")
    return _model


def get_embedding(text: str) -> np.ndarray:
    """
    Generate an embedding for the given text
    
    Args:
        text: Input text to embed
    
    Returns:
        numpy array of the embedding vector
    """
    model = _get_model()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.astype("float32")


def create_or_load_index(project_id: str, dimension: int = 384) -> faiss.IndexFlatL2:
    """
    Create or load a FAISS index for the given project
    
    Args:
        project_id: Project identifier
        dimension: Embedding dimension (384 for all-MiniLM-L6-v2)
    
    Returns:
        FAISS index
    """
    index_path = FAISS_DATA_DIR / f"{project_id}.index"
    
    try:
        if index_path.exists():
            index = faiss.read_index(str(index_path))
            logger.debug(f"Loaded existing FAISS index for project {project_id}")
        else:
            index = faiss.IndexFlatL2(dimension)
            logger.debug(f"Created new FAISS index for project {project_id}")
    except Exception as e:
        logger.error(f"Error loading FAISS index for project {project_id}: {str(e)}")
        # Create a new index if loading fails
        index = faiss.IndexFlatL2(dimension)
    
    return index


def _get_metadata_path(project_id: str) -> Path:
    """Get the metadata file path for a project"""
    return FAISS_DATA_DIR / f"{project_id}.json"


def _load_metadata(project_id: str) -> List[Dict]:
    """Load metadata for a project"""
    metadata_path = _get_metadata_path(project_id)
    try:
        if metadata_path.exists():
            with open(metadata_path, "r") as f:
                return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing metadata JSON for project {project_id}: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Error loading metadata for project {project_id}: {str(e)}")
        return []
    return []


def _save_metadata(project_id: str, metadata: List[Dict]):
    """Save metadata for a project"""
    metadata_path = _get_metadata_path(project_id)
    try:
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving metadata for project {project_id}: {str(e)}")
        raise


async def add_embeddings(
    project_id: str,
    vectors: List[np.ndarray],
    metadata: List[Dict],
):
    """
    Add embeddings to the project's FAISS index and metadata store
    Thread-safe using per-project locks
    
    Args:
        project_id: Project identifier
        vectors: List of embedding vectors (numpy arrays)
        metadata: List of metadata dictionaries (one per vector)
    
    Raises:
        ValueError: If vectors and metadata don't match in length
        Exception: If file operations fail
    """
    if len(vectors) != len(metadata):
        raise ValueError("Number of vectors must match number of metadata entries")
    
    if len(vectors) == 0:
        return
    
    # Get lock for this project
    lock = await _get_lock(project_id)
    
    async with lock:
        try:
            # Load or create index
            dimension = len(vectors[0])
            index = create_or_load_index(project_id, dimension)
            
            # Stack vectors into a matrix
            vectors_matrix = np.vstack(vectors)
            
            # Add to index
            index.add(vectors_matrix)
            logger.debug(f"Added {len(vectors)} embeddings to index for project {project_id}")
            
            # Load existing metadata
            existing_metadata = _load_metadata(project_id)
            
            # Append new metadata
            existing_metadata.extend(metadata)
            
            # Save metadata
            _save_metadata(project_id, existing_metadata)
            
            # Save index
            index_path = FAISS_DATA_DIR / f"{project_id}.index"
            faiss.write_index(index, str(index_path))
            logger.debug(f"Saved FAISS index and metadata for project {project_id}")
        except Exception as e:
            logger.error(f"Error adding embeddings for project {project_id}: {str(e)}")
            raise


def search(project_id: str, query: str, k: int = 5) -> List[Dict]:
    """
    Search for similar code snippets using FAISS
    
    Args:
        project_id: Project identifier
        query: Search query text
        k: Number of results to return
    
    Returns:
        List of metadata dictionaries for top-k matches (empty list if index/metadata don't exist)
    """
    index_path = FAISS_DATA_DIR / f"{project_id}.index"
    metadata_path = _get_metadata_path(project_id)
    
    # Handle missing index file gracefully
    if not index_path.exists():
        logger.debug(f"FAISS index not found for project {project_id}")
        return []
    
    # Handle missing metadata file gracefully
    if not metadata_path.exists():
        logger.debug(f"Metadata file not found for project {project_id}")
        return []
    
    try:
        # Load index and metadata
        index = faiss.read_index(str(index_path))
        metadata = _load_metadata(project_id)
        
        if index.ntotal == 0:
            logger.debug(f"FAISS index for project {project_id} is empty")
            return []
        
        if len(metadata) == 0:
            logger.debug(f"Metadata for project {project_id} is empty")
            return []
        
        # Generate query embedding
        query_embedding = get_embedding(query)
        query_vector = query_embedding.reshape(1, -1)
        
        # Search
        distances, indices = index.search(query_vector, min(k, index.ntotal))
        
        # Return metadata for matched items
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(metadata):
                result = metadata[idx].copy()
                result["score"] = float(distance)  # Lower is better (L2 distance)
                results.append(result)
        
        logger.debug(f"Found {len(results)} results for query in project {project_id}")
        return results
    
    except faiss.FaissException as e:
        logger.error(f"FAISS error searching project {project_id}: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Error searching embeddings for project {project_id}: {str(e)}")
        return []

