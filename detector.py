import os
import json
from pathlib import Path


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
        if content_start.strip().startswith(('<!DOCTYPE html>', '<html', '<HTML')):
            result.update({
                "module": "html_preview",
                "content_type": "text/html",
                "render_mode": "iframe",
                "supports_edit": True,
                "webhook_payload_type": "text"
            })
            return result

        # Mermaid diagram
        if any(pattern in content_start for pattern in ['graph TD', 'graph LR', 'flowchart TD', 'flowchart LR', 'sequenceDiagram', 'classDiagram', 'stateDiagram', 'erDiagram', 'pie']):
            result.update({
                "module": "meirmaid",
                "content_type": "text/mermaid",
                "render_mode": "diagram",
                "supports_edit": True,
                "webhook_payload_type": "text"
            })
            return result

        # Excalidraw
        if '"type": "excalidraw"' in content_start or '"elements":' in content_start:
            result.update({
                "module": "excalidraw",
                "content_type": "application/json",
                "render_mode": "canvas",
                "supports_edit": True,
                "webhook_payload_type": "json"
            })
            return result

        # Ask Question Tool
        if '"type": "askQuestionTool"' in content_start or ('"options":' in content_start and ('[' in content_start)):
            # Valida se é JSON válido
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json.load(f)
                result.update({
                    "module": "claudeCode_askQuestionTool",
                    "content_type": "application/json",
                    "render_mode": "form",
                    "supports_edit": True,
                    "webhook_payload_type": "options"
                })
                return result
            except json.JSONDecodeError:
                pass

        # Kanban
        if '"type": "kanban"' in content_start or ('"columns":' in content_start and '[' in content_start):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json.load(f)
                result.update({
                    "module": "kanban",
                    "content_type": "application/json",
                    "render_mode": "board",
                    "supports_edit": True,
                    "webhook_payload_type": "form"
                })
                return result
            except json.JSONDecodeError:
                pass

        # TodoList
        if '"type": "todolist"' in content_start or '"tasks":' in content_start:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json.load(f)
                result.update({
                    "module": "todolist",
                    "content_type": "application/json",
                    "render_mode": "list",
                    "supports_edit": True,
                    "webhook_payload_type": "form"
                })
                return result
            except json.JSONDecodeError:
                pass

        # Formulário
        if '"type": "formulario"' in content_start or '"fields":' in content_start:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json.load(f)
                result.update({
                    "module": "formulario",
                    "content_type": "application/json",
                    "render_mode": "form",
                    "supports_edit": True,
                    "webhook_payload_type": "form"
                })
                return result
            except json.JSONDecodeError:
                pass

        # Verifica por extensão (fallback)
        ext = Path(file_path).suffix.lower()

        # Extensões específicas
        extension_map = {
            '.html': 'html_preview',
            '.htm': 'html_preview',
            '.mermaid': 'meirmaid',
            '.mmd': 'meirmaid',
            '.excalidraw': 'excalidraw',
            '.json': 'json_editor',
            '.md': 'markdown',
            '.png': 'image_preview',
            '.jpg': 'image_preview',
            '.jpeg': 'image_preview',
            '.gif': 'image_preview',
            '.svg': 'image_preview',
            '.webp': 'image_preview',
        }

        if ext in extension_map:
            module = extension_map[ext]
            if module == 'html_preview':
                result.update({
                    "module": module,
                    "content_type": "text/html",
                    "render_mode": "iframe",
                    "supports_edit": True,
                    "webhook_payload_type": "text"
                })
            elif module == 'meirmaid':
                result.update({
                    "module": module,
                    "content_type": "text/mermaid",
                    "render_mode": "diagram",
                    "supports_edit": True,
                    "webhook_payload_type": "text"
                })
            elif module == 'image_preview':
                result.update({
                    "module": module,
                    "content_type": f"image/{ext[1:]}",
                    "render_mode": "image",
                    "supports_edit": False,
                    "webhook_payload_type": "text"
                })
            elif module == 'json_editor':
                result.update({
                    "module": "json_editor",
                    "content_type": "application/json",
                    "render_mode": "code",
                    "supports_edit": True,
                    "webhook_payload_type": "json"
                })
            elif module == 'markdown':
                result.update({
                    "module": "markdown",
                    "content_type": "text/markdown",
                    "render_mode": "markdown",
                    "supports_edit": True,
                    "webhook_payload_type": "text"
                })
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
    except Exception:
        return {
            "exists": False,
            "error": "Could not get file metadata"
        }
