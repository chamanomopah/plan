seu objetivo é transformar o $arguments do usuario em visualizar arquivos atraves do **Interactive web interface for viewing and editing projects with real-time AI agent collaboration** 


sempre que o usuario pedir pra criar um projeto novo, ele esta se referindo a criar uma pasta e um arquivo dentro dela em projects/  (pois o sistema tem um monitoramento em tempo real pra indetificar arquivos nas pastas)

tbm é ncessario criar um projects/{project_name}/config.json

Project-specific configuration, exemple:

```json
{
  "webhook": "https://your-n8n-instance.com/webhook/plan",
  "display_name": "Hero Page Design",
  "icon": "🎨",
  "module_overrides": {
    "design.html": {
      "module": "html_preview"
    }
  }
}
```
**What it does**: Customizes display name, icon, and which visualization module to use for specific files.

modulos atuais que funcionam corretamente:

├── modulos/                        # Visualization modules
│   ├── html_preview.py            # HTML rendering
│   ├── meirmaid.py                # Mermaid diagrams


skills atuais pra criar o projects/{project_name}/{file_type}

criar meirmaid diagrams : @.claude\skills\mermaid-diagram\SKILL.md

seu trabalho é pensar no pedido do usuario e converter em um arquivo que possa ser visualizado 
