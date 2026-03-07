"""
Módulo de visualização para diagramas Mermaid.
Renderiza diagramas Mermaid em SVG.
"""


def render_mermaid(content: str) -> str:
    """
    Retorna o HTML para renderização do diagrama Mermaid.
    """
    return f"""
    <div class="mermaid-diagram">
        <pre class="mermaid">{escape_html(content)}</pre>
    </div>
    """


def get_user_input_html() -> str:
    """
    Retorna o HTML para o input do usuário na sidebar.
    """
    return """
    <textarea id="userInput" class="user-input-textarea"
              placeholder="Descreva as mudanças que deseja fazer no diagrama..."></textarea>
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
        'name': 'meirmaid',
        'display_name': 'Mermaid Diagram',
        'description': 'Visualização de diagramas Mermaid',
        'supported_extensions': ['.mermaid', '.mmd'],
        'render_mode': 'diagram',
        'supports_edit': True,
        'webhook_payload_type': 'text'
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
