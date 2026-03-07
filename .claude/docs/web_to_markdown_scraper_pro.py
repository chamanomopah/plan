#!/usr/bin/env python3
"""
Web to Markdown Scraper PRO - Enhanced Version
================================================
Script avançado para fazer web scraping e converter conteúdo HTML para Markdown.
Suporta sites estáticos E sites com JavaScript (usando Playwright).

Autor: Claude
Data: 2026-02-26
Versão: 2.1 - Ultra Clean Edition
"""

import sys
import re
import argparse
from pathlib import Path
from typing import Optional

# Reconfigura stdout para UTF-8 no Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

try:
    import requests
    from bs4 import BeautifulSoup
    import html2text
except ImportError as e:
    print(f"[ERROR] Dependency not found: {e}")
    print("\n[INFO] Install required dependencies:")
    print("   pip install requests beautifulsoup4 html2text")
    sys.exit(1)

# Playwright é opcional
PLAYWRIGHT_AVAILABLE = False
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    pass


class WebToMarkdown:
    """Classe principal para converter páginas web para Markdown."""

    def __init__(
        self,
        url: str,
        output_file: Optional[str] = None,
        ignore_images: bool = False,
        body_width: int = 0,  # 0 = sem wrap
        use_javascript: bool = False,
        wait_time: int = 3000,  # ms para esperar JS carregar
    ):
        self.url = url
        self.output_file = output_file
        self.ignore_images = ignore_images
        self.body_width = body_width
        self.use_javascript = use_javascript
        self.wait_time = wait_time

        if use_javascript and not PLAYWRIGHT_AVAILABLE:
            print("[WARN] Playwright not found. Installing...")
            print("[INFO] Run: pip install playwright && playwright install chromium")
            print("[INFO] Falling back to static scraping...")

    def fetch_page_static(self) -> str:
        """Busca o conteúdo da página web (método estático)."""
        print(f"[FETCH] Fetching (static): {self.url}")

        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7',
        })

        try:
            response = session.get(self.url, timeout=30)
            response.raise_for_status()
            print(f"[OK] Status: {response.status_code}")
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to fetch page: {e}")
            sys.exit(1)

    def fetch_page_javascript(self) -> str:
        """Busca o conteúdo da página web (método com JavaScript)."""
        print(f"[FETCH] Fetching (with JavaScript): {self.url}")

        if not PLAYWRIGHT_AVAILABLE:
            print("[ERROR] Playwright not available. Cannot use JavaScript mode.")
            print("[INFO] Install: pip install playwright && playwright install chromium")
            return self.fetch_page_static()

        with sync_playwright() as p:
            try:
                # Usa Chromium (headless)
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                # Navega para a página
                page.goto(self.url, wait_until="networkidle", timeout=30000)

                # Espera um tempo extra para JS carregar
                print(f"[WAIT] Waiting {self.wait_time}ms for JavaScript to load...")
                page.wait_for_timeout(self.wait_time)

                # Obtém o HTML renderizado
                html = page.content()

                browser.close()
                print(f"[OK] Page loaded with JavaScript")
                return html

            except Exception as e:
                print(f"[ERROR] Failed to load page with JavaScript: {e}")
                print("[INFO] Falling back to static scraping...")
                return self.fetch_page_static()

    def clean_html(self, html: str, url: str) -> str:
        """Limpa o HTML removendo elementos desnecessários."""
        soup = BeautifulSoup(html, 'html.parser')

        # 1. Remove scripts, estilos e elementos invisíveis
        for tag in ['script', 'style', 'noscript', 'iframe', 'svg']:
            for element in soup.find_all(tag):
                element.decompose()

        # 2. Remove elementos de navegação e UI (classes comuns)
        unwanted_classes = [
            # Navegação
            'nav', 'navbar', 'navigation', 'menu', 'sidebar', 'header', 'footer',
            # UI elements
            'button', 'btn', 'breadcrumb', 'tabs', 'tab', 'pagination',
            # Search
            'search', 'searchbar',
            # Social
            'social', 'share', 'follow',
            # Comments
            'comments', 'comment',
            # Ads
            'ad', 'advertisement', 'banner',
            # Específicos de documentação
            'table-of-contents', 'toc', 'on-this-page', 'page-nav',
            'skip-link', 'skip-to-content',
        ]

        # Remove por classe
        for class_name in unwanted_classes:
            for element in soup.find_all(class_=re.compile(class_name, re.I)):
                element.decompose()

        # Remove por ID
        for id_name in unwanted_classes:
            for element in soup.find_all(id=re.compile(id_name, re.I)):
                element.decompose()

        # 3. Remove elementos específicos por tags e atributos
        # Remove botões
        for element in soup.find_all(['button', 'input']):
            element.decompose()

        # Remove elementos com role="navigation" ou similar
        for element in soup.find_all(attrs={'role': re.compile(r'navigation|complementary|banner', re.I)}):
            element.decompose()

        # Remove elementos com data-* específicos
        for element in soup.find_all(attrs={'data-testid': re.compile(r'header|footer|nav|sidebar', re.I)}):
            element.decompose()

        # 4. Remove elementos vazios ou só com espaços
        for element in soup.find_all():
            if element.string and element.string.strip() == '' and len(element.contents) <= 1:
                element.decompose()

        # 5. Tenta encontrar o conteúdo principal
        main_content = (
            soup.find('main') or
            soup.find('article') or
            soup.find('div', class_=re.compile(r'main-content|article-content|content-body|doc-content|markdown-body', re.I)) or
            soup.find('div', id=re.compile(r'main-content|article|content-body|docs-content', re.I)) or
            soup.body
        )

        if main_content:
            # Remove elementos filhos indesejados do main_content
            for unwanted in main_content.find_all(['nav', 'aside', 'header', 'footer']):
                unwanted.decompose()

            return str(main_content)

        return str(soup.body) if soup.body else str(soup)

    def post_process_markdown(self, markdown: str) -> str:
        """Pós-processa o Markdown para limpeza ultra agressiva."""
        lines = markdown.split('\n')
        cleaned_lines = []

        # Padrões para linhas indesejadas
        unwanted_patterns = [
            r'^\[!\[.*?\]\]',  # Imagens markdown
            r'^\s*(Copy|Share|Report|Edit|Print|Ask AI|Skip)',  # Botões de ação
            r'^\s*Search\.\.\.$',  # Search placeholder
            r'^\s*Ctrl K',  # Atalhos
            r'^\s*English\s*$',  # Idioma
            r'^\[Skip to',  # Skip links
            r'\[​\]\(<#',  # Links de âncora vazios (zero-width space)
            r'\[\]\(<#.*?>\)',  # Links vazios para âncoras
            r'^\s*On this page\s*$',  # Seção "On this page"
            r'^\s*Navigation\s*$',  # Seção "Navigation"
            r'^\s*\* \[.*?\]\(/\docs/en/.*?\)\s*$',  # Links de documentação
            r'^\s*\[Getting started\]',  # Links de navegação
            r'^\s*\[Build with Claude Code\]',  # Links de navegação
            r'^\s*\[Deployment\]',  # Links de navegação
            r'^\s*\[Administration\]',  # Links de navegação
            r'^\s*\[Configuration\]',  # Links de navegação
            r'^\s*\[Reference\]',  # Links de navegação
            r'^\s*\[Resources\]',  # Links de navegação
            r'^\s*\[Claude Developer Platform\]',  # Links externos
            r'^\s*\[Claude Code on the Web\]',  # Links externos
            r'^\s*\[.*? Docs home page',  # Links de home page
            r'^\s*!\[.*?logo',  # Logos
            r'^\s*!\[US\]',  # Flags
            r'^\s*\[.*?\]\(\s*$',  # Links malformados
            r'^\s{0,2}\d+\s*$',  # Números soltos (step numbers)
            r'\[\]\(#\)',  # Links de âncora vazios
        ]

        skip_next = False
        prev_was_empty_heading = False

        for i, line in enumerate(lines):
            if skip_next:
                skip_next = False
                continue

            # Corrige links com < > ao redor da URL
            line = re.sub(r'\[([^\]]+)\]\(<([^>]+)>\)', r'[\1](\2)', line)
            line = re.sub(r'\]\(<([^>]+)>\)', r'](\1)', line)

            # Pula linhas que correspondem aos padrões indesejados
            unwanted = False
            for pattern in unwanted_patterns:
                if re.match(pattern, line, re.IGNORECASE | re.MULTILINE):
                    unwanted = True
                    break

            # Pula linhas que são só números (steps) seguidas de links vazios
            if line.strip().isdigit() and i + 1 < len(lines):
                next_line = lines[i + 1]
                if re.match(r'^\[\]\(<#\)', next_line.strip()):
                    skip_next = True
                    unwanted = True

            # Remove "Copy page" e similares
            if re.match(r'^\s*Copy\s+(page|code)', line, re.IGNORECASE):
                unwanted = True

            # Remove seções de documentação repetitivas
            if re.match(r'^\s*#####', line):  # Subtítulos de navegação
                # Verifica se as próximas linhas são links
                if i + 3 < len(lines) and all('* [' in lines[j] or lines[j].strip() == '' for j in range(i + 1, min(i + 10, len(lines)))):
                    unwanted = True

            # Remove headings vazios (##, ### sem texto)
            if re.match(r'^#+\s*$', line):
                prev_was_empty_heading = True
                unwanted = True
                continue

            # Remove links de âncora após headings vazios
            if prev_was_empty_heading and re.match(r'^\[​\]\(<#', line):
                unwanted = True
                prev_was_empty_heading = False
                continue

            prev_was_empty_heading = False

            if not unwanted:
                cleaned_lines.append(line)

        # Remove linhas vazias excessivas
        cleaned_text = '\n'.join(cleaned_lines)
        cleaned_text = re.sub(r'\n{4,}', '\n\n\n', cleaned_text)  # Máximo 3 novas linhas

        # Limpa espaços extras
        cleaned_text = re.sub(r'^\s+$', '', cleaned_text, flags=re.MULTILINE)
        cleaned_text = re.sub(r' +', ' ', cleaned_text)  # Espaços múltiplos

        # Remove headings vazios no final
        cleaned_text = re.sub(r'^#+\s*$\n?', '', cleaned_text, flags=re.MULTILINE)

        # Remove espaços antes de negritos
        cleaned_text = re.sub(r'\s+\*\*', '**', cleaned_text)

        # Remove links de âncora isolados ([​](#...))
        cleaned_text = re.sub(r'^\[\u200b\]\(#.*?\)\s*$', '', cleaned_text, flags=re.MULTILINE)
        cleaned_text = re.sub(r'\n\[\u200b\]\(#.*?\)\n', '\n', cleaned_text)

        return cleaned_text.strip()

    def html_to_markdown(self, html: str) -> str:
        """Converte HTML limpo para Markdown."""
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = self.ignore_images
        h.ignore_emphasis = False
        h.body_width = self.body_width
        h.unicode_snob = True
        h.skip_internal_links = False
        # Evita links de âncora internas
        h.inline_links = True
        h.protect_links = True
        h.wrap_links = False

        markdown = h.handle(html)
        return markdown

    def process(self) -> str:
        """Processa a URL e retorna o Markdown."""
        # Busca a página
        if self.use_javascript:
            html = self.fetch_page_javascript()
        else:
            html = self.fetch_page_static()

        # Limpa o HTML
        print("[CLEAN] Cleaning HTML...")
        clean_html = self.clean_html(html, self.url)

        # Converte para Markdown
        print("[CONVERT] Converting to Markdown...")
        markdown = self.html_to_markdown(clean_html)

        # Pós-processa o Markdown
        print("[POST-PROCESS] Ultra-cleaning Markdown...")
        markdown = self.post_process_markdown(markdown)

        # Adiciona cabeçalho com metadata
        header = f"""---
# Scraped from {self.url}
# Generated by web_to_markdown_scraper_pro.py v2.1
# Mode: {'JavaScript' if self.use_javascript else 'Static'}
# Dependencies: {'Playwright + BeautifulSoup' if self.use_javascript and PLAYWRIGHT_AVAILABLE else 'BeautifulSoup'}
---

"""

        final_markdown = header + markdown

        return final_markdown

    def save_or_print(self, markdown: str):
        """Salva em arquivo ou imprime no stdout."""
        if self.output_file:
            output_path = Path(self.output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown)

            file_size = len(markdown)
            size_kb = file_size / 1024
            print(f"[SAVE] Saved to: {output_path}")
            print(f"[INFO] Size: {size_kb:.1f} KB ({file_size:,} bytes)")
        else:
            print("\n" + "=" * 80)
            print(markdown)
            print("=" * 80)


def generate_output_name(url: str, number: int = None) -> str:
    """Gera nome de arquivo organizado baseado na URL (mantém nomes originais)."""
    from urllib.parse import urlparse

    # Extrai o caminho da URL
    parsed = urlparse(url)
    path_parts = [p for p in parsed.path.split('/') if p and p not in ['en', 'docs', 'v', 'api']]

    # Mapeamento apenas para consolidar nomes duplicados (sem tradução)
    name_map = {
        'build-with-claude-code': 'claude-code',
        'slash-commands': 'skills',
        'auto-memory': 'memory',
    }

    # Determina o nome base
    if path_parts:
        last_part = path_parts[-1]
        name = name_map.get(last_part, last_part)
    else:
        name = 'document'

    # Adiciona numeração se fornecida
    if number is not None:
        name = f"{number:02d}-{name}"

    return f"docs/{name}.md"


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description='Web to Markdown Scraper PRO - Converta qualquer página web para Markdown',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  # Simples - estático (mais rápido)
  python web_to_markdown_scraper_pro.py https://example.com -o output.md

  # Com numeração automática (salva em docs/01-nome.md)
  python web_to_markdown_scraper_pro.py https://docs.anthropic.com/en/docs/claude-code/skills --js --number 1

  # Com JavaScript e nome automático
  python web_to_markdown_scraper_pro.py https://docs.anthropic.com/en/docs/claude-code/memory --js --number 2

  # Com tempo de espera customizado
  python web_to_markdown_scraper_pro.py https://example.com --js --wait 5000 -o output.md

  # Sem imagens
  python web_to_markdown_scraper_pro.py https://example.com --no-images -o output.md

Instalação do Playwright (opcional, para sites com JavaScript):
  pip install playwright
  playwright install chromium
        """
    )

    parser.add_argument('url', help='URL da página para converter')
    parser.add_argument('-o', '--output', dest='output_file', help='Arquivo de saída (se não especificado, gera nome automático em docs/)')
    parser.add_argument('-n', '--number', dest='number', type=int, help='Número para ordenação (ex: 1, 2, 3...)')
    parser.add_argument('--js', '--javascript', dest='javascript', action='store_true', help='Usar Playwright para renderizar JavaScript (útil para sites modernos)')
    parser.add_argument('--wait', dest='wait_time', type=int, default=3000, help='Tempo de espera em ms para JavaScript carregar (padrão: 3000)')
    parser.add_argument('--no-images', dest='ignore_images', action='store_true', help='Ignorar imagens na conversão')
    parser.add_argument('--body-width', dest='body_width', type=int, default=0, help='Largura máxima das linhas (0 = sem wrap, padrão: 0)')

    args = parser.parse_args()

    # Gera nome automático se não especificado
    output_file = args.output_file
    if not output_file:
        output_file = generate_output_name(args.url, args.number)

    scraper = WebToMarkdown(
        url=args.url,
        output_file=output_file,
        ignore_images=args.ignore_images,
        body_width=args.body_width,
        use_javascript=args.javascript,
        wait_time=args.wait_time,
    )

    markdown = scraper.process()
    scraper.save_or_print(markdown)


if __name__ == '__main__':
    main()
