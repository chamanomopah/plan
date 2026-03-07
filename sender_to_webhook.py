import asyncio
import httpx
import json
from datetime import datetime
from typing import Dict, Any, Optional
import os


async def send_to_webhook(
    project_name: str,
    file_name: str,
    content: str,
    user_input: Dict[str, Any],
    metadata: Dict[str, Any],
    webhook_url: str,
    timeout: int = 30
) -> Dict[str, Any]:
    """
    Envia dados para o webhook N8N.

    Args:
        project_name: Nome do projeto
        file_name: Nome do arquivo
        content: Conteúdo atual do arquivo
        user_input: Input do usuário (texto, opções, etc)
        metadata: Metadados do arquivo (tipo, módulo, etc)
        webhook_url: URL do webhook para enviar
        timeout: Timeout em segundos

    Returns:
        Dict com status e resposta do webhook
    """

    file_path = f"/projetos/{project_name}/{file_name}"

    payload = {
        "project": project_name,
        "file": file_name,
        "file_path": file_path,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "current_state": {
            "content": content,
            "type": metadata.get("content_type", "unknown")
        },
        "user_input": user_input,
        "metadata": {
            "module": metadata.get("module", "unknown"),
            "supports_edit": metadata.get("supports_edit", False),
            "render_mode": metadata.get("render_mode", "unknown"),
            "webhook_payload_type": metadata.get("webhook_payload_type", "text")
        }
    }

    result = {
        "success": False,
        "status_code": None,
        "response": None,
        "error": None
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                webhook_url,
                json=payload,
                timeout=timeout
            )
            result["status_code"] = response.status_code

            # Tenta ler resposta como JSON
            try:
                result["response"] = response.json()
            except (json.JSONDecodeError, ValueError):
                # Se não for JSON, lê como texto
                result["response"] = response.text

            # Considera sucesso se status for 2xx
            if 200 <= response.status_code < 300:
                result["success"] = True
            else:
                result["error"] = f"HTTP {response.status_code}"

    except asyncio.TimeoutError:
        result["error"] = "Timeout"
    except httpx.HTTPError as e:
        result["error"] = f"Connection error: {str(e)}"
    except Exception as e:
        result["error"] = f"Unexpected error: {str(e)}"

    return result


async def send_with_retry(
    project_name: str,
    file_name: str,
    content: str,
    user_input: Dict[str, Any],
    metadata: Dict[str, Any],
    webhook_url: str,
    max_retries: int = 3,
    timeout: int = 30
) -> Dict[str, Any]:
    """
    Envia para webhook com retry e backoff exponencial.
    """

    for attempt in range(max_retries):
        result = await send_to_webhook(
            project_name=project_name,
            file_name=file_name,
            content=content,
            user_input=user_input,
            metadata=metadata,
            webhook_url=webhook_url,
            timeout=timeout
        )

        if result["success"]:
            return result

        # Se falhou e não é a última tentativa, espera com backoff
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt  # 1s, 2s, 4s
            await asyncio.sleep(wait_time)

    return result


def get_webhook_url(
    webhooks_config: Dict[str, Any],
    project_name: str,
    file_name: Optional[str] = None
) -> str:
    """
    Resolve a URL do webhook baseado na hierarquia de escopos.

    Ordem de prioridade:
    1. Webhook específico do arquivo
    2. Webhook do projeto
    3. Webhook global (fallback)
    """

    # Tenta webhook específico do arquivo
    if file_name and project_name in webhooks_config.get("projects", {}):
        project_config = webhooks_config["projects"][project_name]
        if "files" in project_config and file_name in project_config["files"]:
            file_config = project_config["files"][file_name]
            if "webhook" in file_config:
                return file_config["webhook"]

    # Tenta webhook do projeto
    if project_name in webhooks_config.get("projects", {}):
        project_config = webhooks_config["projects"][project_name]
        if "webhook" in project_config and project_config.get("override_global", False):
            return project_config["webhook"]

    # Fallback para webhook global
    return webhooks_config.get("global", {}).get("default_webhook", "")


def load_webhooks_config(config_path: str = "webhooks.json") -> Dict[str, Any]:
    """
    Carrega configuração de webhooks do arquivo JSON.
    """
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Retorna configuração padrão se arquivo não existe
            return {
                "global": {
                    "default_webhook": "",
                    "timeout": 30,
                    "retry_attempts": 3
                },
                "projects": {}
            }
    except Exception as e:
        print(f"Error loading webhooks config: {e}")
        return {
            "global": {
                "default_webhook": "",
                "timeout": 30,
                "retry_attempts": 3
            },
            "projects": {}
        }
