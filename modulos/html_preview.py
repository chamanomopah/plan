"""
Módulo de visualização para HTML.
Renderiza HTML em iframe sandbox.
"""


def render_html(content: str) -> str:
    """
    Retorna o HTML para renderização em iframe.
    """
    # Injeta CSS base para preview
    base_css = """
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            line-height: 1.6;
        }
        img {
            max-width: 100%;
            height: auto;
        }
        table {
            border-collapse: collapse;
            width: 100%;
        }
        table, th, td {
            border: 1px solid #ddd;
        }
        th, td {
            padding: 8px;
            text-align: left;
        }
    </style>
    """

    # Insere CSS se tiver <head>
    if '<head>' in content:
        content = content.replace('<head>', f'<head>{base_css}')
    elif '<html>' in content:
        content = content.replace('<html>', f'<html><head>{base_css}</head>')
    else:
        # Se não tiver <head> ou <html>, envolve com HTML básico
        content = f"""
        <!DOCTYPE html>
        <html>
        <head>{base_css}</head>
        <body>{content}</body>
        </html>
        """

    return content


def get_user_input_html() -> str:
    """
    Retorna o HTML para o input do usuário na sidebar.
    """
    return """
    <textarea id="userInput" class="user-input-textarea"
              placeholder="Descreva as mudanças que deseja fazer no HTML..."></textarea>
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
        'name': 'html_preview',
        'display_name': 'HTML Preview',
        'description': 'Visualização de arquivos HTML',
        'supported_extensions': ['.html', '.htm'],
        'render_mode': 'iframe',
        'supports_edit': True,
        'webhook_payload_type': 'text'
    }
