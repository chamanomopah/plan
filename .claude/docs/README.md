# Web to Markdown Scraper PRO

Script avançado em Python para fazer web scraping e converter páginas HTML para formato Markdown.

## 📁 Estrutura do Projeto

```
└── docs/                             # Exemplos de saída
    ├── 01_anthropic_skills.md       # Skills - Documentação raspada
    ├── 02_anthropic_sub_agents.md   # Sub-agents - Documentação raspada
    └── 03_anthropic_overview.md     # Overview - Documentação raspada
    ├── web_to_markdown_scraper_pro.py   # Script principal
    ├── README.md                         # Este arquivo
```

## 🚀 Uso Rápido

### Instalação
```bash
pip install requests beautifulsoup4 html2text
```

### Exemplo Básico
```bash
python web_to_markdown_scraper_pro.py https://example.com -o output.md
```

### Com JavaScript (sites modernos)
```bash
pip install playwright && playwright install chromium

python web_to_markdown_scraper_pro.py https://docs.anthropic.com --js -o docs.md
```

## 📖 Opções Disponíveis

```bash
python web_to_markdown_scraper_pro.py [URL] [OPÇÕES]

Opções:
  -o, --output      Arquivo de saída (default: stdout)
  --js              Usar Playwright para sites com JavaScript
  --wait            Tempo de espera para JS (ms, default: 3000)
  --ignore-images   Ignorar imagens na conversão
  --body-width      Largura do texto (0 = sem wrap, default: 0)
  -v, --verbose     Modo verboso
```

## ✅ Características

- ✅ Suporte a sites estáticos (BeautifulSoup)
- ✅ Suporte a sites com JavaScript (Playwright)
- ✅ Conversão HTML → Markdown preservando formatação
- ✅ Extração inteligente de conteúdo principal
- ✅ Metadata automática nos arquivos gerados
- ✅ Universal - funciona com qualquer site
- ✅ User-Agent configurável para evitar bloqueios
- ✅ Suporte a UTF-8 no Windows

## 📄 Exemplos de Uso

### Site simples
```bash
python web_to_markdown_scraper_pro.py https://example.com -o example.md
```

### Site com JavaScript
```bash
python web_to_markdown_scraper_pro.py https://docs.anthropic.com --js -o anthropic.md
```

### Múltiplas páginas
```bash
python web_to_markdown_scraper_pro.py https://site.com/page1 --js -o page1.md
python web_to_markdown_scraper_pro.py https://site.com/page2 --js -o page2.md
```

## 🧪 Exemplos de Saída

Veja a pasta `docs/` para exemplos de documentação raspada:
- `01_anthropic_skills.md` - Skills do Claude Code
- `02_anthropic_sub_agents.md` - Sub-agentes do Claude Code
- `03_anthropic_overview.md` - Visão geral do Claude Code

## 📄 Licença

Script criado por Claude - 2026

---

**Versão 2.1 - Ultra Clean Edition**
