"""
Módulo de visualização para diagramas Excalidraw.
Renderiza diagramas Excalidraw (JSON).
"""


import json


def render_excalidraw(content: str) -> str:
    """
    Retorna o HTML para renderização do diagrama Excalidraw.
    """
    try:
        data = json.loads(content)

        # Exibe informações sobre o diagrama
        element_count = len(data.get('elements', []))
        app_state = data.get('appState', {})
        theme = app_state.get('theme', 'light')

        html = '<div class="excalidraw-diagram">'
        html += f'<div class="excalidraw-info">'
        html += f'<p><strong>Excalidraw Diagram</strong></p>'
        html += f'<p>Elements: {element_count}</p>'
        html += f'<p>Theme: {theme}</p>'
        html += f'</div>'
        html += '<p class="text-muted">Preview Excalidraw would render here</p>'
        html += '</div>'

        return html

    except json.JSONDecodeError:
        return f'<pre>{escape_html(content)}</pre>'


def get_user_input_html() -> str:
    """
    Retorna o HTML para o input do usuário na sidebar.
    """
    return """
    <textarea id="userInput" class="user-input-textarea"
              placeholder="Descreva as mudanças que deseja fazer no diagrama Excalidraw..."></textarea>
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
        'name': 'excalidraw',
        'display_name': 'Excalidraw Diagram',
        'description': 'Visualização de diagramas Excalidraw',
        'supported_extensions': ['.excalidraw', '.json'],
        'render_mode': 'canvas',
        'supports_edit': True,
        'webhook_payload_type': 'json'
    }


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
