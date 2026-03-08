from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import json
from pathlib import Path
from typing import Dict, Set
import asyncio
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import uvicorn

from detector import detect_file_type, get_file_content, get_file_metadata
from sender_to_webhook import send_with_retry, get_webhook_url, load_webhooks_config

app = FastAPI(title="Project Viewer", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Store active WebSocket connections
active_connections: Dict[str, Set[WebSocket]] = {}


def _load_project_config(project_name: str) -> dict:
    """Load project configuration from config.json file."""
    config_file = Path(f"projetos/{project_name}/config.json")
    if not config_file.exists():
        return {}

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError, OSError):
        return {}


def _apply_module_overrides(detection: dict, project_config: dict, file_name: str) -> dict:
    """Apply module overrides from project config to detection result."""
    if not project_config or "module_overrides" not in project_config:
        return detection

    if file_name in project_config["module_overrides"]:
        override = project_config["module_overrides"][file_name]
        if "module" in override:
            detection["module"] = override["module"]

    return detection


async def _handle_subscribe(websocket: WebSocket, data: dict) -> tuple:
    """Handle WebSocket subscribe message."""
    project_name = data.get("project")
    file_name = data.get("file")

    if project_name and file_name:
        key = f"{project_name}:{file_name}"
        if key not in active_connections:
            active_connections[key] = set()
        active_connections[key].add(websocket)

        # Confirma inscrição
        await websocket.send_json({
            "type": "subscribed",
            "project": project_name,
            "file": file_name
        })

    return project_name, file_name


async def _handle_unsubscribe(websocket: WebSocket, project_name: str, file_name: str):
    """Handle WebSocket unsubscribe message."""
    if project_name and file_name:
        key = f"{project_name}:{file_name}"
        if key in active_connections:
            active_connections[key].discard(websocket)
            if not active_connections[key]:
                del active_connections[key]

    await websocket.send_json({
        "type": "unsubscribed"
    })


def _remove_connection(websocket: WebSocket, project_name: str, file_name: str):
    """Remove WebSocket connection from active connections."""
    if project_name and file_name:
        key = f"{project_name}:{file_name}"
        if key in active_connections:
            active_connections[key].discard(websocket)
            if not active_connections[key]:
                del active_connections[key]


class FileWatcherHandler(FileSystemEventHandler):
    """
    File watcher para detectar mudanças nos arquivos de projetos.
    """

    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop
        self.last_modified = {}
        self.debounce_delay = 0.5  # 500ms debounce

    def on_modified(self, event):
        if event.is_directory:
            return

        file_path = event.src_path

        # Verifica se está dentro da pasta projetos/
        if "projetos" not in file_path:
            return

        # Debounce: evita múltiplas notificações para o mesmo arquivo
        now = datetime.now().timestamp()
        if file_path in self.last_modified:
            if now - self.last_modified[file_path] < self.debounce_delay:
                return

        self.last_modified[file_path] = now

        # Extrai nome do projeto e arquivo
        try:
            parts = Path(file_path).parts
            if "projetos" in parts:
                projetos_idx = parts.index("projetos")
                if projetos_idx + 1 < len(parts):
                    project_name = parts[projetos_idx + 1]
                    file_name = parts[projetos_idx + 2] if projetos_idx + 2 < len(parts) else None

                    if file_name:
                        # Notifica todos os clientes conectados via WebSocket
                        asyncio.run_coroutine_threadsafe(
                            self.notify_clients(project_name, file_name, file_path),
                            self.loop
                        )
        except Exception as e:
            print(f"Error in file watcher: {e}")

    async def notify_clients(self, project_name: str, file_name: str, file_path: str):
        """
        Notifica todos os clientes conectados sobre a mudança no arquivo.
        """
        try:
            # Detecta tipo de arquivo
            detection = detect_file_type(file_path)

            # Lê conteúdo do arquivo
            content = get_file_content(file_path)

            # Monta mensagem
            message = {
                "type": "file_updated",
                "project": project_name,
                "file": file_name,
                "file_path": file_path,
                "content": content,
                "metadata": detection,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }

            # Envia para todos os clientes conectados
            key = f"{project_name}:{file_name}"
            if key in active_connections:
                for connection in active_connections[key]:
                    try:
                        await connection.send_json(message)
                    except Exception as e:
                        print(f"Error sending to client: {e}")

        except Exception as e:
            print(f"Error notifying clients: {e}")


# Inicia o file watcher
def start_file_watcher(loop: asyncio.AbstractEventLoop):
    """
    Inicia o watchdog observer para monitorar mudanças nos arquivos.
    """
    event_handler = FileWatcherHandler(loop)
    observer = Observer()
    observer.schedule(event_handler, path="projetos", recursive=True)
    observer.start()
    return observer


@app.get("/", response_class=HTMLResponse)
async def root():
    """
    Serve a interface principal.
    """
    try:
        with open("design.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="design.html not found")


@app.get("/api/projects")
async def list_projects():
    """
    Lista todos os projetos disponíveis.
    """
    try:
        projects_path = Path("projetos")
        if not projects_path.exists():
            return []

        projects = []
        for project_dir in projects_path.iterdir():
            if project_dir.is_dir():
                # Tenta carregar config.json do projeto
                config = {}
                config_file = project_dir / "config.json"
                if config_file.exists():
                    try:
                        with open(config_file, 'r', encoding='utf-8') as f:
                            config = json.load(f)
                    except (json.JSONDecodeError, IOError, OSError):
                        pass

                projects.append({
                    "name": project_dir.name,
                    "display_name": config.get("display_name", project_dir.name),
                    "icon": config.get("icon", "📁"),
                    "path": str(project_dir)
                })

        return sorted(projects, key=lambda x: x["name"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects/{project_name}/files")
async def list_project_files(project_name: str):
    """
    Lista todos os arquivos de um projeto.
    """
    try:
        project_path = Path(f"projetos/{project_name}")
        if not project_path.exists():
            raise HTTPException(status_code=404, detail="Project not found")

        files = []
        for file_path in project_path.iterdir():
            if file_path.is_file():
                # Ignora config.json
                if file_path.name == "config.json":
                    continue

                metadata = get_file_metadata(str(file_path))
                detection = detect_file_type(str(file_path))

                files.append({
                    "name": file_path.name,
                    "path": str(file_path),
                    "size": metadata.get("size", 0),
                    "modified": metadata.get("modified", 0),
                    "type": detection.get("module", "unknown"),
                    "content_type": detection.get("content_type", "unknown")
                })

        return sorted(files, key=lambda x: x["name"])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/files/{project_name}/{file_name}")
async def get_file(project_name: str, file_name: str):
    """
    Retorna o conteúdo de um arquivo.
    """
    try:
        file_path = Path(f"projetos/{project_name}/{file_name}")
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        # Detecta tipo de arquivo
        detection = detect_file_type(str(file_path))

        # Lê conteúdo
        content = get_file_content(str(file_path))

        # Carrega config do projeto e aplica overrides
        project_config = _load_project_config(project_name)
        detection = _apply_module_overrides(detection, project_config, file_name)

        return {
            "name": file_name,
            "project": project_name,
            "path": str(file_path),
            "content": content,
            "metadata": detection,
            "detector": detection,  # Added for compatibility with tests
            "size": len(content)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/send-webhook")
async def send_webhook(request: dict):
    """
    Envia dados para o webhook N8N.
    """
    try:
        project_name = request.get("project")
        file_name = request.get("file")
        user_input = request.get("user_input", {})

        if not project_name or not file_name:
            raise HTTPException(status_code=400, detail="Missing project or file")

        # Lê arquivo
        file_path = Path(f"projetos/{project_name}/{file_name}")
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        content = get_file_content(str(file_path))
        detection = detect_file_type(str(file_path))

        # Carrega configuração de webhooks
        webhooks_config = load_webhooks_config()

        # Resolve URL do webhook
        webhook_url = get_webhook_url(webhooks_config, project_name, file_name)

        if not webhook_url:
            raise HTTPException(status_code=400, detail="No webhook configured")

        # Pega timeout da config
        timeout = webhooks_config.get("global", {}).get("timeout", 30)
        retry_attempts = webhooks_config.get("global", {}).get("retry_attempts", 3)

        # Envia para webhook
        result = await send_with_retry(
            project_name=project_name,
            file_name=file_name,
            content=content,
            user_input=user_input,
            metadata=detection,
            webhook_url=webhook_url,
            max_retries=retry_attempts,
            timeout=timeout
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/webhooks/config")
async def get_webhooks_config():
    """
    Retorna a configuração de webhooks.
    """
    try:
        return load_webhooks_config()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _get_module_render_function(module, module_name: str):
    """
    Obtém a função de renderização correta do módulo.
    Lida com variações de nomes de função.
    """
    # Tenta nome específico do módulo primeiro
    render_func_name = f"render_{module_name}"
    render_func = getattr(module, render_func_name, None)

    # Tenta função genérica
    if render_func is None:
        render_func = getattr(module, 'render_html', None)

    # Mapeamentos especiais para inconsistências
    if render_func is None:
        special_mappings = {
            'html_preview': 'render_html_preview',
            'meirmaid': 'render_mermaid',
            'claudeCode_askQuestionTool': 'render_ask_question_tool'
        }
        for module_type, func_name in special_mappings.items():
            if module_name == module_type:
                render_func = getattr(module, func_name, None)
                break

    return render_func


@app.get("/api/modules/{module_name}")
async def get_module_html(module_name: str, content: str = ""):
    """
    Retorna o HTML/JS de um módulo para renderização no frontend.
    """
    try:
        module_path = Path(f"modulos/{module_name}.py")
        if not module_path.exists():
            raise HTTPException(status_code=404, detail="Module not found")

        # Importa o módulo dinamicamente
        import importlib.util
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Chama função de renderização
        render_func = _get_module_render_function(module, module_name)
        visualization_html = ""
        if render_func:
            visualization_html = render_func(content)

        # Chama função de input do usuário
        import inspect
        input_html_func = getattr(module, 'get_user_input_html', None)
        user_input_html = ""
        if input_html_func:
            # Verifica se a função aceita parâmetros
            sig = inspect.signature(input_html_func)
            if len(sig.parameters) > 0:
                user_input_html = input_html_func(content)
            else:
                user_input_html = input_html_func()

        # Retorna informações e HTML renderizado
        return {
            "name": module_name,
            "path": str(module_path),
            "exists": True,
            "visualization_html": visualization_html,
            "user_input_html": user_input_html,
            "module_info": getattr(module, 'get_module_info', lambda: {})()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint para atualizações em tempo real.
    """
    await websocket.accept()
    project_name = None
    file_name = None

    try:
        while True:
            # Recebe mensagem do cliente
            data = await websocket.receive_json()

            message_type = data.get("type")

            if message_type == "subscribe":
                # Cliente se inscreve para receber atualizações de um arquivo
                project_name, file_name = await _handle_subscribe(websocket, data)

            elif message_type == "unsubscribe":
                # Cliente cancela inscrição
                await _handle_unsubscribe(websocket, project_name, file_name)

    except WebSocketDisconnect:
        # Remove conexão da lista de ativas
        _remove_connection(websocket, project_name, file_name)
    except Exception as e:
        print(f"WebSocket error: {e}")


@app.on_event("startup")
async def startup_event():
    """
    Inicia o file watcher quando o servidor iniciar.
    """
    try:
        loop = asyncio.get_event_loop()
        observer = start_file_watcher(loop)

        # Armazena o observer para poder parar no shutdown
        app.state.file_observer = observer
        print("File watcher started successfully")
    except Exception as e:
        print(f"Warning: Could not start file watcher: {e}")
        print("The server will continue without automatic file monitoring")
        app.state.file_observer = None


@app.on_event("shutdown")
async def shutdown_event():
    """
    Para o file watcher quando o servidor desligar.
    """
    if hasattr(app.state, "file_observer") and app.state.file_observer is not None:
        try:
            app.state.file_observer.stop()
            app.state.file_observer.join()
        except Exception as e:
            print(f"Error stopping file watcher: {e}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
