"""
Indexing service - handles AST parsing, symbol extraction, and embedding generation
"""
import json
import logging
from typing import Dict, List, Optional
import os
from pathlib import Path
from services.ast_parser import ASTParser
from services.embedding_service import get_embedding, add_embeddings
from config import BACKEND_DIR

logger = logging.getLogger(__name__)

_ast_parser = ASTParser()
GRAPH_DATA_DIR = BACKEND_DIR / "data" / "graph"
GRAPH_DATA_DIR.mkdir(parents=True, exist_ok=True)


class IndexingService:
    async def index_project(self, project_id: int, project_path: str) -> Dict:
        """Index a project: parse AST, extract symbols, generate embeddings"""
        project_id_str = str(project_id)
        files_indexed = []
        total_symbols = 0
        
        # Collect all symbols and their embeddings
        all_vectors = []
        all_metadata = []
        
        # For call graph: collect all symbols with their calls
        all_symbols_with_calls = []
        
        # Walk through project files
        for root, dirs, files in os.walk(project_path):
            # Skip common ignore directories
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules', '.venv', '.pytest_cache'}]
            
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, project_path)
                
                # Only process Python and JavaScript files for now
                if file.endswith(('.py', '.js')):
                    try:
                        symbols = self._index_file(project_id, file_path, rel_path, all_vectors, all_metadata)
                        
                        # Store symbols with their calls for graph building
                        for symbol in symbols:
                            all_symbols_with_calls.append({
                                "name": symbol.get("name", ""),
                                "file_path": rel_path,
                                "type": symbol.get("type", ""),
                                "calls": symbol.get("calls", [])
                            })
                        
                        files_indexed.append({
                            "path": rel_path,
                            "symbols": len(symbols)
                        })
                        total_symbols += len(symbols)
                    except Exception as e:
                        logger.error(f"Error indexing {rel_path}: {e}")
        
        # Build call graph
        graph = self._build_call_graph(all_symbols_with_calls)
        
        # Save call graph to file
        graph_path = GRAPH_DATA_DIR / f"{project_id_str}.json"
        try:
            with open(graph_path, "w") as f:
                json.dump(graph, f, indent=2)
            logger.info(f"Saved call graph for project {project_id} with {len(graph['symbols'])} symbols and {len(graph['edges'])} edges")
        except Exception as e:
            logger.error(f"Error saving call graph for project {project_id}: {e}")
        
        # Add all embeddings to FAISS index in batch
        if all_vectors:
            await add_embeddings(project_id_str, all_vectors, all_metadata)
        
        return {
            "file_count": len(files_indexed),
            "symbols_extracted": total_symbols,
            "files": files_indexed,
            "graph_symbols": len(graph["symbols"]),
            "graph_edges": len(graph["edges"])
        }
    
    def _index_file(
        self, 
        project_id: int, 
        file_path: str, 
        rel_path: str,
        all_vectors: List,
        all_metadata: List
    ) -> List[Dict]:
        """Index a single file and add embeddings to the batch"""
        language = "python" if file_path.endswith('.py') else "javascript"
        
        # Parse AST and extract symbols
        symbols = _ast_parser.parse_file(file_path, language)
        
        # Generate embeddings for each symbol
        for symbol in symbols:
            symbol["project_id"] = project_id
            symbol["file_path"] = rel_path
            
            # Build text representation for embedding
            text_repr = (
                f"File: {rel_path}\n"
                f"Symbol: {symbol.get('name', 'unknown')}\n"
                f"Type: {symbol.get('type', 'unknown')}\n"
                f"Code:\n{symbol.get('code', '')}"
            )
            
            # Generate embedding
            embedding = get_embedding(text_repr)
            
            # Prepare metadata (store what we need for retrieval)
            metadata = {
                "file_path": rel_path,
                "name": symbol.get("name", ""),
                "type": symbol.get("type", ""),
                "line_start": symbol.get("line_start", 0),
                "line_end": symbol.get("line_end", 0),
                "code": symbol.get("code", ""),
            }
            
            # Add to batch
            all_vectors.append(embedding)
            all_metadata.append(metadata)
        
        return symbols
    
    def _build_call_graph(self, symbols_with_calls: List[Dict]) -> Dict:
        """
        Build a call graph from symbols and their calls
        
        Args:
            symbols_with_calls: List of symbols with their calls information
        
        Returns:
            Dictionary with "symbols" and "edges" keys
        """
        # Assign IDs to symbols
        symbols = []
        symbol_map = {}  # (name, file_path) -> id
        
        for idx, sym in enumerate(symbols_with_calls):
            symbol_id = idx + 1
            key = (sym["name"], sym["file_path"])
            symbol_map[key] = symbol_id
            
            symbols.append({
                "id": symbol_id,
                "name": sym["name"],
                "file_path": sym["file_path"],
                "type": sym["type"]
            })
        
        # Build edges based on calls
        edges = []
        
        for sym in symbols_with_calls:
            symbol_key = (sym["name"], sym["file_path"])
            from_id = symbol_map.get(symbol_key)
            
            if from_id is None:
                continue
            
            # For each call, try to find matching symbols
            for call_name in sym.get("calls", []):
                # Try to find symbols with matching name
                # Match by name only (since we don't know the exact file for external calls)
                for target_sym in symbols_with_calls:
                    target_key = (target_sym["name"], target_sym["file_path"])
                    target_id = symbol_map.get(target_key)
                    
                    # Match if the call name matches the symbol name
                    # This handles both direct matches and method matches (e.g., "create_user" matches "Service.create_user")
                    if target_id and target_id != from_id:
                        # Exact match or method name match
                        if call_name == target_sym["name"] or target_sym["name"].endswith(f".{call_name}"):
                            edges.append({
                                "from": from_id,
                                "to": target_id
                            })
                            # Only add the first match to avoid duplicates
                            break
        
        return {
            "symbols": symbols,
            "edges": edges
        }

