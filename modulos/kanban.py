"""
Módulo de visualização para Kanban boards.
Renderiza boards Kanban (JSON).
"""


import json


def render_kanban(content: str) -> str:
    """
    Retorna o HTML para renderização do Kanban board (read-only).
    """
    try:
        data = json.loads(content)

        html = '<div class="kanban-board">'

        columns = data.get('columns', [])
        for column in columns:
            column_name = column.get('name', 'Unnamed')
            cards = column.get('cards', [])

            html += f'<div class="kanban-column">'
            html += f'<h4>{escape_html(column_name)}</h4>'
            html += '<div class="kanban-cards">'

            for card in cards:
                card_text = card if isinstance(card, str) else card.get('text', str(card))
                html += f'<div class="kanban-card">{escape_html(card_text)}</div>'

            html += '</div></div>'

        html += '</div>'

        return html

    except json.JSONDecodeError:
        return f'<pre>{escape_html(content)}</pre>'


def get_user_input_html(content: str = None) -> str:
    """
    Retorna o HTML para o input do usuário na sidebar.
    """
    try:
        if content:
            data = json.loads(content)
        else:
            data = {}

        html = '<div class="kanban-input">'
        html += '<p style="margin-bottom: 0.75rem; font-size: 0.875rem;">Adicionar novo card:</p>'
        html += '<select id="kanbanColumn" class="user-input-select" style="margin-bottom: 0.5rem;">'

        columns = data.get('columns', [])
        for column in columns:
            column_name = column.get('name', 'Unnamed')
            html += f'<option value="{escape_html(column_name)}">{escape_html(column_name)}</option>'

        html += '</select>'
        html += '<textarea id="userInput" class="user-input-textarea" placeholder="Texto do card..."></textarea>'
        html += '</div>'

        return html

    except json.JSONDecodeError:
        return """
        <textarea id="userInput" class="user-input-textarea"
                  placeholder="Erro ao carregar colunas..."></textarea>
        """


def collect_user_input(post_data: dict, content: str = None) -> dict:
    """
    Coleta e processa o input do usuário.
    """
    column = post_data.get('kanbanColumn', '')
    card_text = post_data.get('userInput', '')

    return {
        'type': 'kanban',
        'data': {
            'action': 'add_card',
            'column': column,
            'card_text': card_text
        }
    }


def get_module_info() -> dict:
    """
    Retorna informações sobre o módulo.
    """
    return {
        'name': 'kanban',
        'display_name': 'Kanban Board',
        'description': 'Visualização de Kanban boards',
        'supported_extensions': ['.txt', '.json'],
        'render_mode': 'board',
        'supports_edit': True,
        'webhook_payload_type': 'form'
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
