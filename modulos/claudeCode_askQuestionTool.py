"""
Módulo de visualização para askQuestionTool (JSON com opções).
Renderiza opções como checkboxes/radio buttons e permite seleção.
"""


import json


def render_ask_question_tool(content: str) -> str:
    """
    Retorna o HTML para renderização das opções (read-only).
    """
    try:
        data = json.loads(content)

        html = '<div class="options-display">'

        # Título da pergunta
        question = data.get('question', 'Selecione as opções:')
        html += f'<h3>{escape_html(question)}</h3>'

        # Lista de opções
        html += '<div class="option-list">'

        options = data.get('options', [])
        for option in options:
            option_id = option.get('id', '')
            option_text = option.get('text', option_id)
            selected = option.get('selected', False)

            selected_class = 'selected' if selected else ''
            checkmark = '✓' if selected else '○'

            html += f"""
            <div class="option-item-display {selected_class}">
                <span>{checkmark}</span>
                <span>{escape_html(option_text)}</span>
            </div>
            """

        html += '</div></div>'

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

        html = '<div class="options-input">'

        # Título da pergunta
        question = data.get('question', 'Selecione as opções:')
        html += f'<p style="margin-bottom: 0.75rem; font-size: 0.875rem;">{escape_html(question)}</p>'

        # Opções de seleção
        options = data.get('options', [])
        allow_multiple = data.get('allow_multiple', True)
        input_type = 'checkbox' if allow_multiple else 'radio'
        input_name = 'askQuestionOptions'

        for option in options:
            option_id = option.get('id', '')
            option_text = option.get('text', option_id)
            selected = option.get('selected', False)

            checked = 'checked' if selected else ''

            html += f"""
            <div class="option-item">
                <input type="{input_type}" name="{input_name}" id="opt_{option_id}"
                       value="{escape_html(option_id)}" {checked}>
                <label for="opt_{option_id}">{escape_html(option_text)}</label>
            </div>
            """

        html += '</div>'

        # Campo de comentário
        html += """
        <textarea id="userInputComment" class="user-input-textarea"
                  placeholder="Adicione um comentário (opcional)..."
                  style="margin-top: 0.75rem;"></textarea>
        """

        return html

    except json.JSONDecodeError:
        return """
        <textarea id="userInput" class="user-input-textarea"
                  placeholder="Erro ao carregar opções..."></textarea>
        """


def collect_user_input(post_data: dict, content: str = None) -> dict:
    """
    Coleta e processa o input do usuário.
    """
    try:
        if content:
            data = json.loads(content)
            allow_multiple = data.get('allow_multiple', True)
        else:
            allow_multiple = True

        # Coleta opções selecionadas
        selected_options = post_data.getlist('askQuestionOptions', []) if allow_multiple else ([post_data.get('askQuestionOptions')] if post_data.get('askQuestionOptions') else [])
        comment = post_data.get('userInputComment', '')

        return {
            'type': 'options',
            'data': {
                'selected': selected_options,
                'comment': comment
            }
        }

    except Exception:
        return {
            'type': 'text',
            'data': post_data.get('userInput', '')
        }


def get_module_info() -> dict:
    """
    Retorna informações sobre o módulo.
    """
    return {
        'name': 'claudeCode_askQuestionTool',
        'display_name': 'Ask Question Tool',
        'description': 'Ferramenta de seleção de opções (JSON)',
        'supported_extensions': ['.txt', '.json'],
        'render_mode': 'form',
        'supports_edit': True,
        'webhook_payload_type': 'options'
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
