# Plano: MVP Interface Interativa para Visualização e Edição de Projetos

## Contexto
Criar uma interface web interativa para visualizar e editar projetos de origens variadas (apps, sites, fluxogramas de workflows de AI, documentação, etc.) de forma simplificada. O usuário visualiza arquivos da pasta `projetos/` através de **módulos especializados de visualização**, envia comandos via webhook para workflows N8N (que usam agentes AI), e o agente edita os arquivos diretamente, com a interface atualizando automaticamente via WebSocket.

**Importante**: N8N é apenas o meio de comunicação entre o usuário e os agentes. Os projetos podem ser de qualquer tipo - sites, aplicativos, fluxogramas, documentação, workflows de AI, etc.

## A Importância dos Módulos de Visualização

Os módulos de visualização são **essenciais e fundamentais** para o sistema. Eles são responsáveis por:

- **Interpretar diferentes tipos de arquivos**: HTML, Mermaid, JSON, YAML, etc.
- **Renderizar visualizações apropriadas**: Cada tipo de arquivo tem sua forma específica de ser apresentado
- **Fornecer interações específicas**: Checkboxes, forms, seleções, visualização de diagramas
- **Capturar inputs do usuário**: Cada módulo sabe como coletar os dados corretos para enviar ao webhook
- **Atualização em tempo real**: Recebem notificações quando o arquivo é modificado pelo agente

Sem os módulos, o sistema não teria como interpretar e visualizar os diferentes tipos de projetos de forma adequada.

## Decisões Técnicas Definidas

✅ **Atualização em Tempo Real**: WebSocket (instantâneo)
✅ **Extensões**: Sem extensão = `.txt`, mas com detecção obrigatória por conteúdo
✅ **Webhooks**: Arquivo `webhooks.json` com escopos (global + por projeto)
✅ **Formato askQuestionTool**: JSON com array de opções e estados
✅ **Backend**: FastAPI (moderno, async nativo)

## Estrutura do Sistema

### Arquivos Principais
```
plan/
├── app.py                          # Servidor FastAPI com WebSocket
├── main.py                         # Entry point (uvicorn)
├── webhooks.json                   # Configuração de webhooks (global + por projeto)
├── design.html                     # Interface principal (barra lateral + visualização)
├── detector.py                     # Detecta tipo de arquivo por CONTEÚDO e extensão
├── sender_to_webhook.py            # Envia requisições para webhooks N8N
├── modulos/                        # Módulos de visualização (ESSENCIAL)
│   ├── html_preview.py            # Preview de HTML
│   ├── meirmaid.py                # Diagramas Mermaid
│   ├── excalidraw.py              # Diagramas Excalidraw
│   ├── claudeCode_askQuestionTool.py  # Seleção de opções (JSON)
│   ├── formulario.py              # Formulários interativos
│   ├── kanban.py                  # Kanban boards
│   ├── todolist.py                # Listas de tarefas
│   └── image_preview.py           # Preview de imagens
└── projetos/                       # Projetos ativos (apps, sites, fluxogramas, etc)
    ├── heroPage_design/           # Projeto: Design de Hero Page
    │   ├── config.json            # Config específica do projeto (opcional)
    │   └── design.html
    ├── qualification_questions/   # Projeto: Questões de Qualificação
    │   ├── config.json            # Config específica (opcional)
    │   ├── askQuestionTool1.txt   # JSON com opções
    │   └── askQuestionToo2.txt    # JSON com opções
    └── sdlcWorkflow_structure/    # Projeto: Estrutura de Workflow SDLC
        ├── config.json            # Config específica (opcional)
        └── structure.meirmaid     # Diagrama Mermaid
```

## Implementação Detalhada

### 1. Detector de Arquivos (`detector.py`)

**Função principal**: `detect_file_type(file_path: str) -> dict`

```python
{
    "module": "nome_do_modulo",
    "content_type": "tipo_conteudo",
    "render_mode": "modo_renderizacao",
    "supports_edit": true/false,
    "webhook_payload_type": "text|options|form|other"
}
```

**Lógica de detecção**:
1. Lê primeiros 1024 bytes do arquivo
2. Detecta padrões de conteúdo:
   - `<!DOCTYPE html>` ou `<html` → HTML
   - `graph TD` ou `flowchart TD` → Mermaid
   - `{"type": "excalidraw"` ou `{"elements":` → Excalidraw
   - `{"type": "askQuestionTool"` ou `{"options":` → askQuestionTool
   - `{"type": "kanban"` ou `{"columns":` → Kanban
   - `{"type": "todolist"` ou `{"tasks":` → TodoList
   - `{"type": "formulario"` ou `{"fields":` → Formulário
3. Valida com extensão se disponível
4. Retorna metadados completos

**Casos especiais**:
- Mesma extensão, conteúdo diferente → usa detector de conteúdo
- Arquivo vazio → retorna módulo "text_editor" padrão

### 2. Interface Principal (`design.html`)

**Layout**:
```
┌───────────────────────────────────────────────────────────────────────────┐
│  [Seletor de Projeto ▼]              Project Viewer           [Reload] │
├─────────────────────────────┬─────────────────────────────────────────────┤
│  SIDEBAR - Configurações    │  VISUALIZAÇÃO (Read-only)                   │
│                             │                                             │
│  Webhook:                   │  ┌─────────────────────────────────────────┐│
│  https://n8n.../webhook     │  │                                         ││
│  [Configurar]               │  │                                         ││
│                             │  │     Preview do Módulo                   ││
│  ─────────────────────      │  │     (HTML / Mermaid / Opções)           ││
│                             │  │                                         ││
│  Seu Input:                 │  │                                         ││
│  ┌───────────────────────┐  │  │                                         ││
│  │                       │  │  │                                         ││
│  │  [Texto ou opções]    │  │  │     [Renderizado pelo Módulo]          ││
│  │  [Adaptável ao tipo]  │  │  │                                         ││
│  │                       │  │  │                                         ││
│  └───────────────────────┘  │  │                                         ││
│                             │  └─────────────────────────────────────────┘│
│  [Enviar para Webhook ►]    │                                             │
│                             │                                             │
│  Arquivos do Projeto:       │                                             │
│  📄 design.html ◀           │                                             │
│  📄 structure.meirmaid      │                                             │
│                             │                                             │
└─────────────────────────────┴─────────────────────────────────────────────┘
```

**Componentes**:

#### Header Superior
1. **Seletor de Projeto** (Dropdown no canto superior esquerdo):
   - Lista todos os projetos disponíveis
   - Ao selecionar, recarrega sidebar com arquivos do projeto
   - Mostra ícone + nome do projeto

2. **Botão Recarregar** (canto superior direito):
   - Recarrega todos os arquivos
   - Reconecta WebSocket se necessário

#### Sidebar (Esquerda) - Apenas Configurações

1. **Configuração de Webhook**:
   - Display do webhook atual do projeto
   - Botão "Configurar" para editar URL
   - Badge mostrando escopo (global/projeto/arquivo)

2. **Área de Input do Usuário** (adaptável pelo módulo):
   - Arquivos HTML/Mermaid: Campo de texto multiline
   - AskQuestionTool: Checkboxes/radio buttons com opções
   - Formulários: Campos específicos do formulário
   - **Cada módulo define seu próprio tipo de input**

3. **Botão Enviar**:
   - Envia input + estado do arquivo para webhook
   - Feedback visual (loading, success, error)

4. **Lista de Arquivos do Projeto**:
   - Lista todos os arquivos do projeto selecionado
   - Indicador de arquivo ativo
   - Click para navegar entre arquivos
   - Badge se arquivo foi modificado

#### Área Principal (Direita) - Apenas Visualização

1. **Header do Arquivo**:
   - Nome do arquivo atual
   - Tipo de arquivo
   - Última modificação

2. **Container de Visualização** (renderizado pelo módulo):
   - **Read-only por padrão** (não-editável)
   - Cada módulo renderiza seu conteúdo de forma específica:
     - HTML: Preview em iframe
     - Mermaid: Diagrama renderizado (com zoom/pan)
     - AskQuestionTool: Lista de opções (read-only)
     - Kanban: Board visual (read-only)
     - TodoList: Lista visual (read-only)

3. **Casos Especiais de Interatividade**:
   - Diagramas Mermaid: Permite arrastar/zoom (não editar conteúdo)
   - Imagens: Zoom
   - Canvas: Visualização interativa (pan/zoom)

4. **SEM inputs de edição** na área de visualização
   - Toda interação de edição/modificação fica na sidebar
   - Área direita é apenas para visualização do resultado

#### WebSocket Client
- Conexão automática ao carregar
- Listener para eventos de atualização
- Re-renderização automática da área de visualização pelo módulo
- Notificação toast quando arquivo é atualizado
- **Sidebar NÃO é recarregada** (preserva input do usuário)

### 3. Webhooks Configuration (`webhooks.json`)

```json
{
  "global": {
    "default_webhook": "https://n8n.example.com/webhook/main",
    "timeout": 30,
    "retry_attempts": 3
  },
  "projects": {
    "heroPage_design": {
      "webhook": "https://n8n.example.com/webhook/design",
      "override_global": true
    },
    "qualification_questions": {
      "webhook": "https://n8n.example.com/webhook/questions",
      "files": {
        "askQuestionTool1": {
          "webhook": "https://n8n.example.com/webhook/ask1"
        }
      }
    }
  }
}
```

**Hierarquia de resolução**:
1. Webhook específico do arquivo (maior prioridade)
2. Webhook do projeto
3. Webhook global (fallback)

### 4. Sender to Webhook (`sender_to_webhook.py`)

**Função**: `send_to_webhook(project_name: str, file_name: str, content: dict, webhook_url: str)`

**Payload enviado**:
```json
{
  "project": "heroPage_design",
  "file": "design.html",
  "file_path": "/projetos/heroPage_design/design.html",
  "timestamp": "2026-03-05T10:30:00Z",
  "current_state": {
    "content": "...",
    "type": "html"
  },
  "user_input": {
    "type": "text|options|form",
    "data": "texto do usuário ou opções selecionadas"
  },
  "metadata": {
    "module": "html_preview",
    "supports_edit": true
  }
}
```

**Tratamento de erros**:
- Timeout
- Webhook inacessível
- Validação de resposta
- Retry com backoff exponencial

### 5. Módulos de Visualização (Componentes Essenciais)

#### html_preview.py
- Renderiza HTML em iframe sandbox
- Atualiza ao receber evento WebSocket
- Injeta CSS base para preview
- **Input na sidebar**: Campo de texto multiline

#### meirmaid.py
- Usa biblioteca mermaid.js
- Converte sintaxe para SVG
- Zoom e pan no diagrama
- **Input na sidebar**: Campo de texto para instruções

#### claudeCode_askQuestionTool.py
- Lê JSON do arquivo
- Formato esperado:
```json
{
  "type": "askQuestionTool",
  "question": "Selecione as opções:",
  "options": [
    {"id": "opt1", "text": "Opção 1", "selected": false},
    {"id": "opt2", "text": "Opção 2", "selected": true}
  ],
  "allow_multiple": true
}
```
- Renderiza checkboxes ou radio buttons na sidebar
- **Visualização (read-only)**: Mostra estado atual das opções
- **Input na sidebar**: Checkboxes/radio buttons interativos + campo de comentário

#### kanban.py
- Lê JSON do arquivo
- Formato esperado:
```json
{
  "type": "kanban",
  "columns": [
    {"name": "To Do", "cards": ["Task 1", "Task 2"]},
    {"name": "In Progress", "cards": ["Task 3"]}
  ]
}
```
- Renderiza kanban visualmente
- **Input na sidebar**: Campos para adicionar/mover cards

#### todolist.py
- Lê JSON do arquivo
- Renderiza lista de tarefas visualmente
- **Input na sidebar**: Campos para adicionar/marcar tarefas

#### formulario.py
- Lê definição do formulário
- Renderiza formulário visualmente
- **Input na sidebar**: Campos do formulário para preenchimento

### 6. Backend FastAPI (`app.py`)

**Endpoints**:

1. `GET /` - Serve a interface principal
2. `GET /api/projects` - Lista todos os projetos
3. `GET /api/projects/{project_name}/files` - Lista arquivos do projeto
4. `GET /api/files/{project_name}/{file_name}` - Retorna conteúdo do arquivo
5. `POST /api/send-webhook` - Envia para webhook N8N
6. `GET /api/modules/{module_name}` - Retorna HTML/JS do módulo para renderização
7. `WS /ws` - WebSocket para atualizações em tempo real

**WebSocket Events**:
```python
# Cliente → Servidor
{"type": "subscribe", "project": "heroPage_design", "file": "design.html"}
{"type": "unsubscribe"}

# Servidor → Cliente
{"type": "file_updated", "project": "...", "file": "...", "content": "...", "module": "..."}
{"type": "error", "message": "..."}
```

**File Watcher**:
- Usa `watchdog` library
- Monitora pasta `projetos/` recursivamente
- Emite evento WebSocket quando arquivo muda
- Debounce de 500ms para evitar múltiplas notificações

### 7. Estrutura de Arquivos de Projeto

**Arquivo config.json (opcional)**:
```json
{
  "webhook": "https://n8n.example.com/webhook/custom",
  "display_name": "Nome Personalizado",
  "icon": "🎨",
  "module_overrides": {
    "design.html": {
      "module": "html_preview"
    }
  }
}
```

## Fluxo Completo de Uso

### 1. Visualização e Edição

```
Usuário → Abre interface
      → WebSocket conecta
      → Seleciona projeto no dropdown superior
      → Sidebar carrega arquivos do projeto
      → Usuário seleciona arquivo na sidebar
      → Detector identifica tipo de arquivo
      → Sistema carrega módulo apropriado
      → Módulo renderiza conteúdo na área direita (read-only)
      → Módulo renderiza input adaptável na sidebar
      → Usuário interage com o input na sidebar
      → Clica em "Enviar" na sidebar
      → sender_to_webhook monta payload com dados do módulo
      → Envia para webhook configurado (N8N)
      → Workflow N8N processa e chama agente AI
      → Agente edita o arquivo
      → File watcher detecta mudança
      → WebSocket notifica todos clientes
      → Módulo re-renderiza área direita automaticamente
      → Sidebar preserva input do usuário (não recarrega)
```

### 2. Exemplos Práticos

#### Exemplo 1: HTML Design (Projeto de Site)
1. Usuário seleciona "heroPage_design" no dropdown superior
2. Sidebar lista arquivos: `design.html`
3. Usuário clica em `design.html`
4. **Detector identifica**: HTML
5. **Módulo html_preview** é carregado
6. **Área direita**: Preview do HTML aparece (read-only)
7. **Sidebar**: Mostra campo de texto + webhook configurado
8. Usuário digita na sidebar: "Mudar cor do header para azul"
9. Clica em "Enviar para Webhook"
10. Sistema envia HTML atual + input do usuário
11. Agente AI (via N8N) edita o arquivo HTML
12. **Apenas área direita** atualiza com novo HTML
13. **Sidebar preserva** o texto digitado (caso queira enviar novamente)

#### Exemplo 2: Ask Question Tool (Projeto de Qualificação)
1. Usuário seleciona "qualification_questions" no dropdown
2. Sidebar lista: `askQuestionTool1`, `askQuestionToo2`
3. Usuário clica em `askQuestionTool1.txt`
4. **Detector identifica**: askQuestionTool (JSON)
5. **Módulo claudeCode_askQuestionTool** é carregado
6. **Área direita**: Mostra opções do JSON (read-only, visualização)
7. **Sidebar**: Mostra checkboxes interativos + campo de comentário
8. Usuário marca opções na sidebar
9. Adiciona comentário: "Considerar essas prioridades"
10. Clica em "Enviar"
11. Sistema envia opções selecionadas + comentário
12. Agente AI atualiza JSON do arquivo
13. **Área direita** atualiza com novo estado
14. **Sidebar preserva** seleções e comentário

#### Exemplo 3: Mermaid Diagram (Projeto de Workflow)
1. Usuário seleciona "sdlcWorkflow_structure" no dropdown
2. Sidebar lista: `structure.meirmaid`
3. Usuário clica no arquivo
4. **Detector identifica**: Mermaid
5. **Módulo meirmaid** é carregado
6. **Área direita**: Diagrama renderizado (zoom/pan permitidos)
7. **Sidebar**: Campo de texto para instruções
8. Usuário digita: "Adicionar etapa de deploy após testing"
9. Clica em "Enviar"
10. Sistema envia diagrama atual + instrução
11. Agente AI modifica arquivo Mermaid
12. **Área direita** atualiza diagrama
13. **Sidebar preserva** texto da instrução

## Dependências Principais

```python
# requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
websockets==12.0
watchdog==3.0.0
aiohttp==3.9.1
python-multipart==0.0.6
jinja2==3.1.2
```

## Frontend Dependencies

```javascript
// Via CDN na interface
- mermaid.js (diagramas)
- marked.js (markdown, se necessário)
- highlight.js (syntax highlighting)
```

## Implementação - Ordem de Execução

### Fase 1: Base (Core)
1. ✅ Estrutura de pastas e arquivos
2. `webhooks.json` com estrutura de escopos
3. `app.py` - FastAPI básico com WebSocket
4. `detector.py` - Detecção por conteúdo

### Fase 2: Interface
5. `design.html` - Layout base (sidebar + main)
6. WebSocket client no frontend
7. Listagem de projetos e arquivos
8. Navegação entre arquivos

### Fase 3: Módulos Principais (Essencial)
9. `html_preview.py` - Preview de HTML
10. `meirmaid.py` - Diagramas Mermaid
11. `claudeCode_askQuestionTool.py` - Seleção de opções

### Fase 4: Integração
12. `sender_to_webhook.py` - Envio para N8N
13. File watcher no backend
14. Sistema de escopos de webhooks
15. Testes end-to-end

### Fase 5: Módulos Secundários
16. `kanban.py` - Kanban boards
17. `todolist.py` - Listas de tarefas
18. `formulario.py` - Formulários
19. `excalidraw.py` - Diagramas Excalidraw
20. `image_preview.py` - Preview de imagens
21. Melhorias de UX
22. Documentação

## Arquivos Críticos a Modificar/Criar

### Novos Arquivos
- `app.py` - Backend FastAPI
- `main.py` - Entry point
- `webhooks.json` - Configuração de webhooks
- `requirements.txt` - Dependências Python
- `static/js/websocket.js` - Cliente WebSocket
- `static/css/main.css` - Estilos da interface

### Arquivos a Implementar
- `design.html` - Interface principal
- `detector.py` - Detector de conteúdo
- `sender_to_webhook.py` - Cliente HTTP
- `modulos/*.py` - Todos os módulos de visualização (ESSENCIAL)

### Arquivos de Dados
- Criar arquivos de exemplo em `projetos/` com conteúdo real
- Criar `webhooks.json` com estrutura de escopos

## Verificação e Testes

### Teste 1: Atualização em Tempo Real
1. Iniciar servidor
2. Abrir interface em 2 abas
3. Modificar arquivo manualmente
4. Verificar atualização instantânea nas 2 abas

### Teste 2: Detecção de Conteúdo
1. Criar arquivo .txt com HTML
2. Criar arquivo .txt com JSON de opções
3. Verificar detecção correta em cada caso

### Teste 3: Escopos de Webhook
1. Configurar webhook global
2. Configurar webhook específico por projeto
3. Configurar webhook específico por arquivo
4. Verificar resolução correta da hierarquia

### Teste 4: Envio para Webhook
1. Configurar URL de teste: `https://maceio-n8n-alfa42.serveousercontent.com/webhook/plan`
2. Enviar payload da interface
3. Verificar que o payload contém todas as informações necessárias:
   - Nome do projeto
   - Nome do arquivo
   - Caminho completo do arquivo
   - Estado atual do arquivo (conteúdo)
   - Input do usuário (texto, opções, etc.)
   - Timestamp
   - Metadados (tipo de arquivo, módulo usado)

**Nota**: As configurações do workflow N8N são responsabilidade do usuário. O sistema apenas garante que o payload correto seja enviado para a URL configurada.

### Teste 5: Módulos de Visualização
1. Testar cada módulo com seu tipo de arquivo específico
2. Verificar renderização correta na área direita
3. Verificar input adaptável na sidebar
4. Verificar atualização automática quando arquivo é modificado

## URL de Teste

Para testes iniciais, usar:
```
https://maceio-n8n-alfa42.serveousercontent.com/webhook/plan
```

## Próximos Passos

Aguardando aprovação do plano para iniciar implementação.
