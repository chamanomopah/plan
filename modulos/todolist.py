"""
Módulo de visualização para Todo Lists.
Renderiza listas de tarefas (JSON).
"""


import json


def render_todolist(content: str) -> str:
    """
    Retorna o HTML para renderização da todo list (read-only).
    """
    try:
        data = json.loads(content)

        html = '<div class="todolist-container">'

        tasks = data.get('tasks', [])
        if tasks:
            html += '<ul class="todolist-items">'

            for task in tasks:
                if isinstance(task, dict):
                    task_text = task.get('text', 'Unnamed')
                    completed = task.get('completed', False)
                else:
                    task_text = str(task)
                    completed = False

                completed_class = 'completed' if completed else ''
                checkmark = '✓' if completed else '○'

                html += f"""
                <li class="todolist-item {completed_class}">
                    <span>{checkmark}</span>
                    <span>{escape_html(task_text)}</span>
                </li>
                """

            html += '</ul>'
        else:
            html += '<p class="text-muted">Nenhuma tarefa</p>'

        html += '</div>'

        return html

    except json.JSONDecodeError:
        return f'<pre>{escape_html(content)}</pre>'


def get_user_input_html(content: str = None) -> str:
    """
    Retorna o HTML para o input do usuário na sidebar.
    """
    html = '<div class="todolist-input">'
    html += '<p style="margin-bottom: 0.75rem; font-size: 0.875rem;">Adicionar nova tarefa:</p>'
    html += '<textarea id="userInput" class="user-input-textarea" placeholder="Descrição da tarefa..."></textarea>'
    html += '</div>'

    return html


def collect_user_input(post_data: dict, content: str = None) -> dict:
    """
    Coleta e processa o input do usuário.
    """
    task_text = post_data.get('userInput', '')

    return {
        'type': 'todolist',
        'data': {
            'action': 'add_task',
            'task_text': task_text
        }
    }


def get_module_info() -> dict:
    """
    Retorna informações sobre o módulo.
    """
    return {
        'name': 'todolist',
        'display_name': 'Todo List',
        'description': 'Visualização de listas de tarefas',
        'supported_extensions': ['.txt', '.json'],
        'render_mode': 'list',
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
