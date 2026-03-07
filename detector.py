import os
import json
from pathlib import Path
from typing import Dict, Any, Optional


def _validate_json_file(file_path: str) -> bool:
    """Check if a file contains valid JSON."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json.load(f)
        return True
    except (json.JSONDecodeError, IOError, OSError):
        return False


def _detect_html_by_content(content_start: str) -> Optional[Dict[str, Any]]:
    """Detect HTML files by content."""
    if content_start.strip().startswith(('<!DOCTYPE html>', '<html', '<HTML')):
        return {
            "module": "html_preview",
            "content_type": "text/html",
            "render_mode": "iframe",
            "supports_edit": True,
            "webhook_payload_type": "text"
        }
    return None


def _detect_mermaid_by_content(content_start: str) -> Optional[Dict[str, Any]]:
    """Detect Mermaid diagrams by content."""
    mermaid_patterns = [
        'graph TD', 'graph LR', 'flowchart TD', 'flowchart LR',
        'sequenceDiagram', 'classDiagram', 'stateDiagram', 'erDiagram',
        'pie'
    ]
    if any(pattern in content_start for pattern in mermaid_patterns):
        return {
            "module": "meirmaid",
            "content_type": "text/mermaid",
            "render_mode": "diagram",
            "supports_edit": True,
            "webhook_payload_type": "text"
        }
    return None


def _detect_excalidraw_by_content(content_start: str) -> Optional[Dict[str, Any]]:
    """Detect Excalidraw files by content."""
    if '"type": "excalidraw"' in content_start or '"elements":' in content_start:
        return {
            "module": "excalidraw",
            "content_type": "application/json",
            "render_mode": "canvas",
            "supports_edit": True,
            "webhook_payload_type": "json"
        }
    return None


def _detect_json_type_by_content(content_start: str, file_path: str) -> Optional[Dict[str, Any]]:
    """Detect JSON-based file types by content."""
    # Ask Question Tool
    has_ask_question = '"type": "askQuestionTool"' in content_start
    has_options_pattern = '"options":' in content_start and '[' in content_start
    if has_ask_question or has_options_pattern:
        if _validate_json_file(file_path):
            return {
                "module": "claudeCode_askQuestionTool",
                "content_type": "application/json",
                "render_mode": "form",
                "supports_edit": True,
                "webhook_payload_type": "options"
            }

    # Kanban
    has_kanban = '"type": "kanban"' in content_start
    has_columns = '"columns":' in content_start and '[' in content_start
    if has_kanban or has_columns:
        if _validate_json_file(file_path):
            return {
                "module": "kanban",
                "content_type": "application/json",
                "render_mode": "board",
                "supports_edit": True,
                "webhook_payload_type": "form"
            }

    # TodoList
    if '"type": "todolist"' in content_start or '"tasks":' in content_start:
        if _validate_json_file(file_path):
            return {
                "module": "todolist",
                "content_type": "application/json",
                "render_mode": "list",
                "supports_edit": True,
                "webhook_payload_type": "form"
            }

    # Formulário
    if '"type": "formulario"' in content_start or '"fields":' in content_start:
        if _validate_json_file(file_path):
            return {
                "module": "formulario",
                "content_type": "application/json",
                "render_mode": "form",
                "supports_edit": True,
                "webhook_payload_type": "form"
            }

    return None


def _detect_by_extension(file_path: str) -> Optional[Dict[str, Any]]:
    """Detect file type based on extension."""
    ext = Path(file_path).suffix.lower()

    extension_map = {
        '.html': ('html_preview', 'text/html', 'iframe', 'text'),
        '.htm': ('html_preview', 'text/html', 'iframe', 'text'),
        '.mermaid': ('meirmaid', 'text/mermaid', 'diagram', 'text'),
        '.mmd': ('meirmaid', 'text/mermaid', 'diagram', 'text'),
        '.excalidraw': ('excalidraw', 'application/json', 'canvas', 'json'),
        '.json': ('json_editor', 'application/json', 'code', 'json'),
        '.md': ('markdown', 'text/markdown', 'markdown', 'text'),
        '.png': ('image_preview', 'image/png', 'image', 'text'),
        '.jpg': ('image_preview', 'image/jpeg', 'image', 'text'),
        '.jpeg': ('image_preview', 'image/jpeg', 'image', 'text'),
        '.gif': ('image_preview', 'image/gif', 'image', 'text'),
        '.svg': ('image_preview', 'image/svg+xml', 'image', 'text'),
        '.webp': ('image_preview', 'image/webp', 'image', 'text'),
    }

    if ext in extension_map:
        module, content_type, render_mode, payload_type = extension_map[ext]
        supports_edit = module != 'image_preview'
        return {
            "module": module,
            "content_type": content_type,
            "render_mode": render_mode,
            "supports_edit": supports_edit,
            "webhook_payload_type": payload_type
        }

    return None


def detect_file_type(file_path: str) -> dict:
    """
    Detecta o tipo de arquivo baseado em CONTEÚDO e extensão.

    Retorna um dicionário com metadados sobre o arquivo.
    """
    result = {
        "module": "text_editor",
        "content_type": "text/plain",
        "render_mode": "text",
        "supports_edit": True,
        "webhook_payload_type": "text",
        "error": None
    }

    try:
        # Verifica se arquivo existe
        if not os.path.exists(file_path):
            result["error"] = "File not found"
            return result

        # Verifica se está vazio
        if os.path.getsize(file_path) == 0:
            return result

        # Lê primeiros bytes para detecção de conteúdo
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content_start = f.read(2048)

        # Detecta por padrões de CONTEÚDO
        # HTML
        html_result = _detect_html_by_content(content_start)
        if html_result:
            result.update(html_result)
            return result

        # Mermaid diagram
        mermaid_result = _detect_mermaid_by_content(content_start)
        if mermaid_result:
            result.update(mermaid_result)
            return result

        # Excalidraw
        excalidraw_result = _detect_excalidraw_by_content(content_start)
        if excalidraw_result:
            result.update(excalidraw_result)
            return result

        # JSON-based types
        json_result = _detect_json_type_by_content(content_start, file_path)
        if json_result:
            result.update(json_result)
            return result

        # Detecta por extensão (fallback)
        extension_result = _detect_by_extension(file_path)
        if extension_result:
            result.update(extension_result)
            return result

        # Padrão: editor de texto
        return result

    except Exception as e:
        result["error"] = str(e)
        return result


def get_file_content(file_path: str) -> str:
    """
    Lê o conteúdo do arquivo de forma segura.
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"


def get_file_metadata(file_path: str) -> dict:
    """
    Retorna metadados do arquivo.
    """
    try:
        stat = os.stat(file_path)
        return {
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "created": stat.st_ctime,
            "exists": True
        }
    except (OSError, IOError):
        return {
            "exists": False,
            "error": "Could not get file metadata"
        }
