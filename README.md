# N8N Project Viewer

**Interactive web interface for viewing and editing projects with real-time AI agent collaboration**

## What It Does

This web application lets you visualize and edit project files through specialized modules. When you make changes, they're sent to N8N workflows where AI agents process your requests and update the files directly. The interface automatically refreshes to show the changes.

Think of it as a collaborative editor where you work alongside AI agents to modify websites, workflows, diagrams, and documents.

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- N8N webhook URL (for AI agent integration)

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```bash
# Start the server
python main.py
```

The interface will be available at: **http://localhost:8000**

## How It Works

The system connects three components:

1. **Web Interface**: You view files and provide input through specialized visualization modules
2. **N8N Webhook**: Your input is sent to N8N workflows where AI agents process it
3. **File Updates**: AI agents modify files directly, and WebSocket instantly updates your view

**Key Components:**

- **Visualization Modules**: Each file type has a specialized renderer (HTML preview, diagrams, forms, kanban boards, etc.)
- **Real-time Updates**: WebSocket pushes file changes immediately when AI agents modify them
- **Webhook Integration**: Send commands to N8N workflows with user input and file context
- **File Watcher**: Monitors project folders for changes and broadcasts them to connected clients

## Real Use Cases

### Use Case 1: Edit a Website Design

**Scenario**: You want to modify the hero section of a landing page with AI assistance.

**Steps**:
1. Open the interface at `http://localhost:8000`
2. Select the `heroPage_design` project from the sidebar
3. Click on `design.html` to see the HTML preview
4. In the input form, describe your changes: "Make the headline larger and add a gradient background"
5. Click "Send to Webhook"
6. Wait for the AI agent to process your request
7. Watch the interface update automatically with the new design

**Result**: The HTML file is updated by the AI agent, and you see the changes immediately in the preview.

### Use Case 2: Manage a Kanban Workflow

**Scenario**: You need to update tasks in a project workflow diagram.

**Steps**:
1. Select the `qualification_questions` project
2. Open `kanban.json` to see the Kanban board visualization
3. Add new tasks or move existing cards
4. Submit your changes via webhook
5. The AI agent updates the JSON structure
6. The Kanban board refreshes automatically

**Result**: Your workflow is updated, and the JSON file reflects the new state.

### Use Case 3: Collaborate on Documentation

**Scenario**: Multiple AI agents are updating documentation files in real-time.

**Steps**:
1. Open any project with markdown or text files
2. Subscribe to real-time updates via WebSocket
3. As AI agents make changes, see updates instantly without refreshing
4. Make your own edits and send them for processing

**Result**: Collaborative editing with AI agents processing requests simultaneously.

## Configuration

### webhooks.json

Defines webhook URLs for different projects and files:

```json
{
  "global": {
    "default_webhook": "https://your-n8n-instance.com/webhook/plan",
    "timeout": 30,
    "retry_attempts": 3
  },
  "projects": {
    "heroPage_design": {
      "webhook": "https://your-n8n-instance.com/webhook/plan",
      "override_global": true
    },
    "qualification_questions": {
      "webhook": "https://your-n8n-instance.com/webhook/plan",
      "files": {
        "askQuestionTool1": {
          "webhook": "https://your-n8n-instance.com/webhook/special"
        }
      }
    }
  }
}
```

**What it does**: Sets default webhook URLs and allows per-project or per-file overrides.

### projects/{project_name}/config.json

Project-specific configuration:

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

## Project Structure

```
plan/
├── main.py                         # Server entry point
├── app.py                          # FastAPI application with WebSocket
├── design.html                     # Main web interface
├── detector.py                     # File type detection by content
├── sender_to_webhook.py            # Webhook communication
├── webhooks.json                   # Webhook configuration
├── requirements.txt                # Python dependencies
├── modulos/                        # Visualization modules
│   ├── html_preview.py            # HTML rendering
│   ├── meirmaid.py                # Mermaid diagrams
│   ├── excalidraw.py              # Excalidraw diagrams
│   ├── claudeCode_askQuestionTool.py  # Interactive options
│   ├── formulario.py              # Form rendering
│   ├── kanban.py                  # Kanban boards
│   ├── todolist.py                # Task lists
│   └── image_preview.py           # Image preview
├── projetos/                       # Your project files
│   ├── heroPage_design/           # Example: Website design
│   ├── qualification_questions/   # Example: Form project
│   └── sdlcWorkflow_structure/    # Example: Workflow diagrams
├── static/                        # Static assets (CSS, JS)
├── tests/                         # Test files
└── docs/                          # Documentation
```

**Important Files:**

- `app.py`: Main server with WebSocket support and API endpoints
- `detector.py`: Analyzes file content to determine the right visualization module
- `webhooks.json`: Configure where to send AI agent requests
- `modulos/*.py`: Each file handles a specific content type (HTML, Mermaid, Kanban, etc.)

## Common Tasks

### Add a New Project

**How to do it**: Create a folder in `projetos/` with your files and optional config.

**Example**:
```bash
# Create project folder
mkdir projetos/my_new_project

# Add your files
cp my_file.html projetos/my_new_project/

# Optional: Add config.json
cat > projetos/my_new_project/config.json << EOF
{
  "display_name": "My New Project",
  "icon": "🚀",
  "webhook": "https://your-n8n-instance.com/webhook/plan"
}
EOF
```

### Create a Custom Visualization Module

**How to do it**: Add a new Python file in `modulos/` with render and input functions.

**Example**:
```python
# modulos/my_custom_module.py
def get_module_info():
    return {
        "name": "My Custom Module",
        "description": "Visualizes custom file format"
    }

def render_html(content):
    return f"<div class='custom-view'>{content}</div>"

def get_user_input_html(content=""):
    return "<textarea name='custom_input'></textarea>"
```

### Configure Webhooks for Specific Files

**How to do it**: Edit `webhooks.json` to add file-specific webhook URLs.

**Example**:
```json
{
  "projects": {
    "my_project": {
      "files": {
        "special_file.json": {
          "webhook": "https://different-webhook.com/process"
        }
      }
    }
  }
}
```

### Run on Different Port

**How to do it**: Modify `main.py` or pass environment variables.

**Example**:
```python
# In main.py, change the port
uvicorn.run(
    "app:app",
    host="0.0.0.0",
    port=8080,  # Change from 8000
    reload=True
)
```

## Troubleshooting

### Server Won't Start

**Symptom**: `Address already in use` error

**Solution**: Another process is using port 8000. Either stop it or change the port in `main.py`.

### Files Not Updating in Real-Time

**Symptom**: Changes to files aren't reflected automatically

**Solution**: Check that:
1. WebSocket connection is established (browser console)
2. File watcher is running (check "File watcher started" message in server logs)
3. Files are in the `projetos/` directory

### Webhook Returns 404

**Symptom**: "No webhook configured" error

**Solution**: Verify `webhooks.json` exists and contains valid URLs for your project/file.

### Module Not Found

**Symptom**: "Module not found" error when opening a file

**Solution**: Ensure the module file exists in `modulos/` and matches the detected file type. Check `detector.py` for how files are mapped to modules.

## Tips & Best Practices

- **Organize projects logically**: Each project in `projetos/` should represent a distinct work item
- **Use descriptive names**: Set `display_name` in config.json for better UX
- **Test webhooks first**: Verify your N8N workflow works before integrating
- **Monitor file changes**: Check server logs for file watcher activity
- **Backup important files**: AI agents will modify files directly - keep backups
- **Use specific modules**: Override auto-detection in config.json for better rendering

## Need Help?

- Check `docs/` directory for additional documentation
- Review `specs/` for implementation details and feature specifications
- See `tests/` for usage examples and expected behavior
