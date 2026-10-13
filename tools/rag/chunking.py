"""AST-Aware Python Code Chunker for FlakyGuard-AI.

Parses Python source files using the standard library ast module to produce semantically
grounded chunks (classes, methods, functions, module-level docstrings) with structural
metadata (docstrings, parameters, decorators, line ranges).
"""

import ast
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class CodeChunk:
    chunk_id: str
    file_path: str
    name: str
    chunk_type: str  # "function", "async_function", "class", "method", "module_docstring"
    content: str
    docstring: Optional[str]
    start_line: int
    end_line: int
    parameters: List[str] = field(default_factory=list)
    decorators: List[str] = field(default_factory=list)
    parent_class: Optional[str] = None

    def to_metadata(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "file_path": self.file_path,
            "name": self.name,
            "chunk_type": self.chunk_type,
            "docstring": self.docstring or "",
            "start_line": self.start_line,
            "end_line": self.end_line,
            "parameters": self.parameters,
            "decorators": self.decorators,
            "parent_class": self.parent_class or "",
        }

    def to_searchable_text(self) -> str:
        """Construct dense text representation optimized for semantic embedding."""
        parts = [
            f"File: {self.file_path}",
            f"{self.chunk_type.replace('_', ' ').title()}: {self.name}",
        ]
        if self.parent_class:
            parts.append(f"Class: {self.parent_class}")
        if self.parameters:
            parts.append(f"Arguments: {', '.join(self.parameters)}")
        if self.docstring:
            parts.append(f"Docstring: {self.docstring}")
        parts.append(f"Code:\n{self.content}")
        return "\n".join(parts)


class ASTChunker:
    """Extracts structural semantic units from Python source trees."""

    def __init__(self, min_lines: int = 1):
        self.min_lines = min_lines

    def chunk_code(self, source_code: str, file_path: str = "<string>") -> List[CodeChunk]:
        """Parse source code into AST chunks."""
        chunks: List[CodeChunk] = []
        source_lines = source_code.splitlines()

        try:
            tree = ast.parse(source_code, filename=file_path)
        except SyntaxError:
            # Fallback to module-level block if file has syntax errors
            return [
                CodeChunk(
                    chunk_id=f"{file_path}:L1-L{len(source_lines)}",
                    file_path=file_path,
                    name=Path(file_path).stem,
                    chunk_type="raw_block",
                    content=source_code,
                    docstring=None,
                    start_line=1,
                    end_line=len(source_lines),
                )
            ]

        # 1. Module Docstring
        mod_doc = ast.get_docstring(tree)
        if mod_doc:
            chunks.append(
                CodeChunk(
                    chunk_id=f"{file_path}:module_docstring",
                    file_path=file_path,
                    name=f"{Path(file_path).stem}_doc",
                    chunk_type="module_docstring",
                    content=mod_doc,
                    docstring=mod_doc,
                    start_line=1,
                    end_line=min(15, len(source_lines)),
                )
            )

        # 2. Iterate AST top-level nodes
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                chunks.append(self._process_function(node, source_lines, file_path))
            elif isinstance(node, ast.ClassDef):
                chunks.extend(self._process_class(node, source_lines, file_path))

        # 3. If file has no functions/classes, record full module
        if not chunks:
            chunks.append(
                CodeChunk(
                    chunk_id=f"{file_path}:module",
                    file_path=file_path,
                    name=Path(file_path).stem,
                    chunk_type="module",
                    content=source_code,
                    docstring=mod_doc,
                    start_line=1,
                    end_line=len(source_lines),
                )
            )

        return chunks

    def chunk_file(self, file_path: str) -> List[CodeChunk]:
        """Read and chunk a Python source file from disk."""
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")

        source_code = path.read_text(encoding="utf-8", errors="replace")
        rel_path = file_path.replace("\\", "/")
        return self.chunk_code(source_code, file_path=rel_path)

    def chunk_directory(
        self,
        directory: str,
        extensions: tuple = (".py",),
        ignore_dirs: tuple = ("venv", ".venv", "__pycache__", ".git", "build", "dist"),
    ) -> List[CodeChunk]:
        """Recursively chunk all matching files in a directory."""
        all_chunks: List[CodeChunk] = []
        root_path = Path(directory)

        for current_root, dirs, files in os.walk(root_path):
            # Prune ignored directories in-place
            dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith(".")]

            for file in files:
                if file.endswith(extensions):
                    full_path = Path(current_root) / file
                    try:
                        all_chunks.extend(self.chunk_file(str(full_path)))
                    except Exception:
                        continue

        return all_chunks

    def _process_function(
        self,
        node: Any,
        lines: List[str],
        file_path: str,
        parent_class: Optional[str] = None,
    ) -> CodeChunk:
        """Extract a function or method chunk."""
        start = node.lineno
        end = getattr(node, "end_lineno", start)
        content = "\n".join(lines[start - 1 : end])
        docstring = ast.get_docstring(node)

        # Extract parameters
        params = [arg.arg for arg in node.args.args]

        # Extract decorator names
        decorators = []
        for dec in node.decorator_list:
            if isinstance(dec, ast.Name):
                decorators.append(dec.id)
            elif isinstance(dec, ast.Attribute):
                decorators.append(f"{getattr(dec.value, 'id', '')}.{dec.attr}")
            elif isinstance(dec, ast.Call):
                func = getattr(dec, "func", None)
                if isinstance(func, ast.Name):
                    decorators.append(func.id)

        chunk_type = "async_function" if isinstance(node, ast.AsyncFunctionDef) else "function"
        if parent_class:
            chunk_type = "method"

        chunk_id = (
            f"{file_path}:{parent_class}.{node.name}"
            if parent_class
            else f"{file_path}:{node.name}"
        )

        return CodeChunk(
            chunk_id=chunk_id,
            file_path=file_path,
            name=node.name,
            chunk_type=chunk_type,
            content=content,
            docstring=docstring,
            start_line=start,
            end_line=end,
            parameters=params,
            decorators=decorators,
            parent_class=parent_class,
        )

    def _process_class(
        self, node: ast.ClassDef, lines: List[str], file_path: str
    ) -> List[CodeChunk]:
        """Extract class definition summary and its inner methods."""
        chunks: List[CodeChunk] = []
        start = node.lineno
        end = getattr(node, "end_lineno", start)
        docstring = ast.get_docstring(node)

        # 1. Class-level summary chunk
        class_header_lines = []
        for i in range(start - 1, min(start + 10, len(lines))):
            class_header_lines.append(lines[i])
            if lines[i].strip().endswith(":") and "class " in lines[i]:
                break

        chunks.append(
            CodeChunk(
                chunk_id=f"{file_path}:{node.name}",
                file_path=file_path,
                name=node.name,
                chunk_type="class",
                content="\n".join(class_header_lines),
                docstring=docstring,
                start_line=start,
                end_line=end,
                parameters=[],
                decorators=[ast.unparse(dec) for dec in node.decorator_list if hasattr(ast, "unparse")],
                parent_class=None,
            )
        )

        # 2. Methods
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                chunks.append(
                    self._process_function(
                        item, lines, file_path, parent_class=node.name
                    )
                )

        return chunks


# Global chunker instance
ast_chunker = ASTChunker()
