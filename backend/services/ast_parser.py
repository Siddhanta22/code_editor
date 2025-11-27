"""
AST Parser service - extracts symbols (functions, classes, methods) from code
"""
import ast
from typing import List, Dict, Set
from pathlib import Path


class ASTParser:
    def parse_file(self, file_path: str, language: str = "python") -> List[Dict]:
        """Parse a file and extract symbols"""
        if language == "python":
            return self._parse_python(file_path)
        elif language == "javascript":
            # Stub for JS parsing (will use tree-sitter later)
            return []
        else:
            return []
    
    def extract_calls(self, node: ast.AST) -> Set[str]:
        """
        Extract function/method call names from an AST node
        
        Args:
            node: AST node to analyze
        
        Returns:
            Set of called function/method names
        """
        calls = set()
        
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                func = child.func
                
                if isinstance(func, ast.Name):
                    # Direct function call: function_name()
                    calls.add(func.id)
                elif isinstance(func, ast.Attribute):
                    # Method call: obj.method_name() or module.function_name()
                    calls.add(func.attr)
        
        return calls
    
    def _parse_python(self, file_path: str) -> List[Dict]:
        """Parse Python file using built-in ast module"""
        symbols = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=file_path)
            
            # Only visit top-level nodes to avoid duplicates
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.FunctionDef):
                    calls = self.extract_calls(node)
                    symbols.append({
                        "type": "function",
                        "name": node.name,
                        "line_start": node.lineno,
                        "line_end": node.end_lineno or node.lineno,
                        "code": ast.get_source_segment(content, node) or "",
                        "calls": list(calls),
                    })
                elif isinstance(node, ast.ClassDef):
                    # Add class definition
                    class_code = ast.get_source_segment(content, node) or ""
                    symbols.append({
                        "type": "class",
                        "name": node.name,
                        "line_start": node.lineno,
                        "line_end": node.end_lineno or node.lineno,
                        "code": class_code,
                        "calls": [],  # Classes don't make calls directly
                    })
                    
                    # Also extract methods from the class
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_calls = self.extract_calls(item)
                            method_code = ast.get_source_segment(content, item) or ""
                            symbols.append({
                                "type": "method",
                                "name": f"{node.name}.{item.name}",
                                "line_start": item.lineno,
                                "line_end": item.end_lineno or item.lineno,
                                "code": method_code,
                                "calls": list(method_calls),
                            })
                        elif isinstance(item, ast.AsyncFunctionDef):
                            method_calls = self.extract_calls(item)
                            method_code = ast.get_source_segment(content, item) or ""
                            symbols.append({
                                "type": "async_method",
                                "name": f"{node.name}.{item.name}",
                                "line_start": item.lineno,
                                "line_end": item.end_lineno or item.lineno,
                                "code": method_code,
                                "calls": list(method_calls),
                            })
                elif isinstance(node, ast.AsyncFunctionDef):
                    calls = self.extract_calls(node)
                    symbols.append({
                        "type": "async_function",
                        "name": node.name,
                        "line_start": node.lineno,
                        "line_end": node.end_lineno or node.lineno,
                        "code": ast.get_source_segment(content, node) or "",
                        "calls": list(calls),
                    })
        
        except SyntaxError as e:
            print(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
        
        return symbols

