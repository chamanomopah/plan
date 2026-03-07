# Claude Code CLI - Referência Rápida

## Comandos Principais

### Inicialização
```bash
# Criar novo projeto
claude-code init

# Iniciar sessão interativa
claude-code chat

# Obter ajuda
claude-code --help
```

### Comandos de Arquivo

| Comando | Alias | Descrição |
|---------|-------|-----------|
| `/read <path>` | - | Ler arquivo |
| `/write <path>` | - | Escrever arquivo |
| `/edit <path>` | - | Editar arquivo |
| `/glob <pattern>` | - | Buscar arquivos por padrão |
| `/grep <pattern>` | - | Buscar conteúdo |

### Comandos de Sistema

| Comando | Descrição |
|---------|-----------|
| `/bash <command>` | Executar comando shell |
| `/run <script>` | Executar script |
| `/test` | Executar testes |
| `/build` | Build do projeto |
| `/lint` | Executar linter |

### Comandos de Controle

| Comando | Descrição |
|---------|-----------|
| `/clear` | Limpar contexto |
| `/history` | Ver histórico |
| `/settings` | Configurações |
| `/exit` | Sair |

### Comandos de Skills

| Comando | Descrição |
|---------|-----------|
| `/skills` | Listar skills disponíveis |
| `/skill <name>` | Executar skill específica |
| `/add-skill` | Adicionar nova skill |
| `/edit-skill <name>` | Editar skill |

### Comandos de Memória

| Comando | Descrição |
|---------|-----------|
| `/remember <note>` | Salvar nota na memória |
| `/memory` | Ver memória atual |
| `/forget <pattern>` | Remover da memória |

### Comandos Git

| Comando | Descrição |
|---------|-----------|
| `/status` | Status do git |
| `/commit` | Criar commit |
| `/push` | Push para remoto |
| `/pull` | Pull do remoto |
| `/branch` | Gerenciar branches |

### Comandos de Projeto

| Comando | Descrição |
|---------|-----------|
| `/plan <task>` | Criar plano de implementação |
| `/implement <plan>` | Implementar plano |
| `/review` | Revisar código |
| `/refactor <path>` | Refatorar código |

## Flags Globais

| Flag | Descrição |
|------|-----------|
| `-v, --verbose` | Saída detalhada |
| `-q, --quiet` | Saída silenciosa |
| `-y, --yes` | Auto-confirmar |
| `--dry-run` | Simular execução |
| `--help` | Ajuda do comando |
| `--version` | Versão da CLI |

## Arquivos de Configuração

### CLAUDE.md
Instruções do projeto (raiz)

```markdown
# Nome do Projeto
Descrição breve

## Comandos
npm run build
npm test

## Arquitetura
- src/ - Código fonte
- tests/ - Testes
```

### .claude/rules/*.md
Regras específicas por caminho

```markdown
---
paths: ["src/api/**/*.ts"]
---

# Regras de API
- Valide entrada com zod
- Retorne erro consistente
```

### .claude/skills/*.md
Skills personalizadas

```markdown
# Minha Skill

## Quando Usar
Quando o usuário pedir X

## Como Funciona
1. Passo 1
2. Passo 2
```

### .claude/commands/*.md
Comandos personalizados

```markdown
# /meu-comando

Descrição do comando

## Uso
/meu-comando <arg1> <arg2>
```

## Hooks

### SessionStart
Executa ao iniciar sessão

### UserPromptSubmit
Executa antes de processar prompt

### PreResponse
Executa antes de responder

## Variáveis de Ambiente

| Variável | Descrição |
|----------|-----------|
| `$CLAUDE_API_KEY` | API Key do Claude |
| `$CLAUDE_MODEL` | Modelo padrão (sonnet/opus/haiku) |
| `$CLAUDE_PLUGIN_ROOT` | Root de plugins |
| `$CLAUDE_MEMORY_DIR` | Diretório de memória |

## Padrões de Uso

### Workflow Típico
```bash
# 1. Iniciar projeto
claude-code init

# 2. Configurar memória
/remember "Usar TypeScript strict"

# 3. Criar feature
/plan "Adicionar autenticação"

# 4. Implementar
/implement plano.md

# 5. Testar
/test

# 6. Commit
/commit
```

### Debugging
```bash
# Ver logs recentes
bash tail -f logs/app.log

# Buscar erros
grep -r "ERROR" src/

# Ver status
/status
```

## Integrações

### MCP (Model Context Protocol)
```bash
# Listar servidores MCP
claude-code mcp list

# Adicionar servidor
claude-code mcp add <name> <config>

# Remover servidor
claude-code mcp remove <name>
```

### Plugins
```bash
# Listar plugins
claude-code plugin list

# Instalar plugin
claude-code plugin install <name>

# Atualizar plugin
claude-code plugin update <name>
```

## Atalhos

| Tecla | Ação |
|-------|------|
| `Ctrl+C` | Cancelar operação |
| `Ctrl+D` | Sair |
| `Ctrl+L` | Limpar tela |
| `Tab` | Auto-completar |
| `↑/↓` | Navegar histórico |

## Recursos

- [Documentação Oficial](https://docs.anthropic.com/claude-code)
- [GitHub](https://github.com/anthropics/claude-code)
- [Community](https://community.anthropic.com)
