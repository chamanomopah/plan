"""
Módulo de visualização para formulários.
Renderiza formulários interativos (JSON).
"""


import json


def render_formulario(content: str) -> str:
    """
    Retorna o HTML para renderização do formulário (read-only).
    """
    try:
        data = json.loads(content)

        html = '<div class="formulario-display">'

        # Título do formulário
        title = data.get('title', 'Formulário')
        html += f'<h3>{escape_html(title)}</h3>'

        # Campos do formulário
        fields = data.get('fields', [])
        html += '<div class="formulario-fields">'

        for field in fields:
            field_label = field.get('label', 'Unnamed')
            field_type = field.get('type', 'text')
            field_value = field.get('value', '')

            html += f'<div class="form-field-display">'
            html += f'<label>{escape_html(field_label)}</label>'

            if field_type == 'textarea':
                html += f'<div class="form-value">{escape_html(field_value) or "<em>Vazio</em>"}</div>'
            elif field_type == 'select':
                options = field.get('options', [])
                selected_label = next((opt.get('label') for opt in options if opt.get('value') == field_value), field_value)
                html += f'<div class="form-value">{escape_html(selected_label) or "<em>Não selecionado</em>"}</div>'
            elif field_type == 'checkbox':
                checked = 'Sim' if field_value else 'Não'
                html += f'<div class="form-value">{checked}</div>'
            else:
                html += f'<div class="form-value">{escape_html(field_value) or "<em>Vazio</em>"}</div>'

            html += '</div>'

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

        html = '<div class="formulario-input">'

        # Título do formulário
        title = data.get('title', 'Preencha o formulário')
        html += f'<p style="margin-bottom: 0.75rem; font-size: 0.875rem;">{escape_html(title)}</p>'

        # Campos do formulário
        fields = data.get('fields', [])

        for field in fields:
            field_name = field.get('name', f'field_{len(fields)}')
            field_label = field.get('label', 'Unnamed')
            field_type = field.get('type', 'text')
            field_value = field.get('value', '')
            required = field.get('required', False)
            required_mark = ' *' if required else ''

            html += f'<div class="form-field" style="margin-bottom: 0.75rem;">'
            html += f'<label for="field_{field_name}" style="display: block; margin-bottom: 0.25rem; font-size: 0.875rem;">{escape_html(field_label)}{required_mark}</label>'

            if field_type == 'textarea':
                html += f'<textarea id="field_{field_name}" name="{field_name}" class="user-input-textarea" rows="3">{escape_html(field_value)}</textarea>'
            elif field_type == 'select':
                html += f'<select id="field_{field_name}" name="{field_name}" class="user-input-select">'
                options = field.get('options', [])
                for option in options:
                    opt_value = option.get('value', '')
                    opt_label = option.get('label', opt_value)
                    selected = 'selected' if opt_value == field_value else ''
                    html += f'<option value="{escape_html(opt_value)}" {selected}>{escape_html(opt_label)}</option>'
                html += '</select>'
            elif field_type == 'checkbox':
                checked = 'checked' if field_value else ''
                html += f'<input type="checkbox" id="field_{field_name}" name="{field_name}" {checked}>'
            else:
                html += f'<input type="text" id="field_{field_name}" name="{field_name}" class="user-input-text" value="{escape_html(field_value)}">'

            html += '</div>'

        html += '</div>'

        return html

    except json.JSONDecodeError:
        return """
        <textarea id="userInput" class="user-input-textarea"
                  placeholder="Erro ao carregar formulário..."></textarea>
        """


def collect_user_input(post_data: dict, content: str = None) -> dict:
    """
    Coleta e processa o input do usuário.
    """
    try:
        if content:
            data = json.loads(content)
        else:
            data = {}

        # Coleta valores dos campos
        fields = data.get('fields', [])
        form_data = {}

        for field in fields:
            field_name = field.get('name', '')
            field_type = field.get('type', 'text')

            if not field_name:
                continue

            if field_type == 'checkbox':
                form_data[field_name] = post_data.get(field_name, False)
            else:
                form_data[field_name] = post_data.get(field_name, '')

        return {
            'type': 'form',
            'data': form_data
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
        'name': 'formulario',
        'display_name': 'Formulário',
        'description': 'Visualização de formulários interativos',
        'supported_extensions': ['.txt', '.json'],
        'render_mode': 'form',
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
