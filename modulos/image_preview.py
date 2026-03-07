"""
Módulo de visualização para imagens.
Renderiza preview de imagens com zoom.
"""


import base64
from pathlib import Path


def render_image(content: str, file_path: str = None) -> str:
    """
    Retorna o HTML para renderização da imagem.
    """
    # Determina o tipo de imagem
    ext = Path(file_path).suffix.lower() if file_path else ''
    mime_type = _get_mime_type(ext)

    html = '<div class="image-preview">'
    html += f'<img src="{file_path}" alt="Preview" class="preview-image" style="max-width: 100%; height: auto;">'
    html += '<p class="text-muted" style="margin-top: 0.5rem;">Zoom: Clique na imagem para ampliar</p>'
    html += '</div>'

    return html


def get_user_input_html() -> str:
    """
    Retorna o HTML para o input do usuário na sidebar.
    """
    return """
    <textarea id="userInput" class="user-input-textarea"
              placeholder="Descreva as mudanças que deseja fazer..."></textarea>
    """


def collect_user_input(post_data: dict) -> dict:
    """
    Coleta e processa o input do usuário.
    """
    user_text = post_data.get('userInput', '')

    return {
        'type': 'text',
        'data': user_text
    }


def get_module_info() -> dict:
    """
    Retorna informações sobre o módulo.
    """
    return {
        'name': 'image_preview',
        'display_name': 'Image Preview',
        'description': 'Visualização de imagens',
        'supported_extensions': ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'],
        'render_mode': 'image',
        'supports_edit': False,
        'webhook_payload_type': 'text'
    }


def _get_mime_type(extension: str) -> str:
    """
    Retorna o MIME type baseado na extensão.
    """
    mime_types = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.svg': 'image/svg+xml',
        '.webp': 'image/webp'
    }
    return mime_types.get(extension.lower(), 'image/png')


def escape_html(text: str) -> str:
    """
    Escapa caracteres HTML para exibição segura.
    """
    html_escape_table = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
    }
    return ''.join(html_escape_table.get(c, c) for c in text)
