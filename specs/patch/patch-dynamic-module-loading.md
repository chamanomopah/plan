# Patch: Enable Dynamic Module Loading from Python to Frontend

## Metadata
- Review Change Request: Frontend doesn't integrate with Python modules - JavaScript has hardcoded rendering logic instead of calling /api/modules/{module_name} to get HTML from Python modules
- Spec Path: specs/MVP Interface Interativa.md

## Issue Summary
**Problem**: The `/api/modules/{module_name}` endpoint (app.py:384-404) only returns metadata about the module, not the actual rendered HTML/JS. The frontend (main.js:184-196) has hardcoded rendering functions for only 3 of 8 modules (html_preview, meirmaid, claudeCode_askQuestionTool), leaving 5 modules (kanban, todolist, formulario, excalidraw, image_preview) non-functional. The spec defines modules with `render_html()` and `get_user_input_html()` functions that should be called dynamically.

**Solution**: Update the `/api/modules/{module_name}` endpoint to import and call the Python module's render functions, returning generated HTML to the frontend. Update frontend to call this endpoint for all modules, making Python modules the single source of truth for rendering logic.

## Files to Modify

- `app.py`: Update `/api/modules/{module_name}` endpoint to import module and call render functions
- `static/js/main.js`: Update `renderFileContent()` and `renderUserInput()` to call `/api/modules/{module_name}` endpoint

## Implementation Steps

IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Update `/api/modules/{module_name}` endpoint in app.py

Replace lines 384-404 in app.py with code that:
1. Imports the module dynamically
2. Calls the module's `render_html()` function (or `render_*()` function) to get visualization HTML
3. Calls the module's `get_user_input_html()` function to get sidebar input HTML
4. Returns both HTML strings to the frontend

**Exact change needed:**

```python
@app.get("/api/modules/{module_name}")
async def get_module_html(module_name: str, content: str = ""):
    """
    Retorna o HTML/JS de um módulo para renderização no frontend.
    """
    try:
        module_path = Path(f"modulos/{module_name}.py")
        if not module_path.exists():
            raise HTTPException(status_code=404, detail="Module not found")

        # Importa o módulo dinamicamente
        import importlib.util
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Chama função de renderização (nome da função varia por módulo)
        render_func_name = f"render_{module_name}"
        render_func = getattr(module, render_func_name, None)
        if render_func is None:
            # Tenta função genérica 'render_html'
            render_func = getattr(module, 'render_html', None)

        visualization_html = ""
        if render_func:
            visualization_html = render_func(content)

        # Chama função de input do usuário
        input_html_func = getattr(module, 'get_user_input_html', None)
        user_input_html = ""
        if input_html_func:
            user_input_html = input_html_func(content)

        # Retorna informações e HTML renderizado
        return {
            "name": module_name,
            "path": str(module_path),
            "exists": True,
            "visualization_html": visualization_html,
            "user_input_html": user_input_html,
            "module_info": getattr(module, 'get_module_info', lambda: {})()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Step 2: Update frontend `renderFileContent()` function in static/js/main.js

Replace lines 180-197 in main.js with code that:
1. Calls `/api/modules/{module_name}` endpoint with current content
2. Uses returned `visualization_html` for rendering
3. Falls back to existing hardcoded logic if endpoint fails

**Exact change needed:**

```javascript
async function renderFileContent(fileData) {
    const container = document.getElementById('visualizationContainer');
    const module = fileData.metadata.module;

    try {
        // Try dynamic module loading first
        const response = await fetch(`${API_BASE}/api/modules/${module}?content=${encodeURIComponent(fileData.content)}`);
        if (response.ok) {
            const moduleData = await response.json();
            if (moduleData.visualization_html) {
                container.innerHTML = moduleData.visualization_html;
                return;
            }
        }
    } catch (error) {
        console.error('Error loading module HTML:', error);
    }

    // Fallback to hardcoded rendering
    switch (module) {
        case 'html_preview':
            renderHTMLPreview(fileData.content, container);
            break;
        case 'meirmaid':
            await renderMermaidDiagram(fileData.content, container);
            break;
        case 'claudeCode_askQuestionTool':
            renderAskQuestionTool(fileData.content, container);
            break;
        default:
            renderTextContent(fileData.content, container);
    }
}
```

### Step 3: Update frontend `renderUserInput()` function in static/js/main.js

Replace lines 260-271 in main.js with code that:
1. Calls `/api/modules/{module_name}` endpoint with current content
2. Uses returned `user_input_html` for rendering
3. Falls back to existing hardcoded logic if endpoint fails

**Exact change needed:**

```javascript
async function renderUserInput(fileData) {
    const container = document.getElementById('userInputContainer');
    const module = fileData.metadata.module;

    try {
        // Try dynamic module loading first
        const response = await fetch(`${API_BASE}/api/modules/${module}?content=${encodeURIComponent(fileData.content)}`);
        if (response.ok) {
            const moduleData = await response.json();
            if (moduleData.user_input_html) {
                container.innerHTML = moduleData.user_input_html;
                return;
            }
        }
    } catch (error) {
        console.error('Error loading module input HTML:', error);
    }

    // Fallback to hardcoded rendering
    switch (module) {
        case 'claudeCode_askQuestionTool':
            renderAskQuestionToolInput(fileData.content, container);
            break;
        default:
            renderDefaultInput(container);
    }
}
```

### Step 4: Fix function signature issue in Python modules

Some modules have inconsistent function names. Create a shim in app.py to handle naming variations:

Add this helper function before the endpoint (around line 380):

```python
def _get_module_render_function(module, module_name: str):
    """
    Obtém a função de renderização correta do módulo.
    Lida com variações de nomes de função.
    """
    # Tenta nome específico do módulo primeiro
    render_func_name = f"render_{module_name}"
    render_func = getattr(module, render_func_name, None)

    # Tenta função genérica
    if render_func is None:
        render_func = getattr(module, 'render_html', None)

    # Mapeamentos especiais para inconsistências
    if render_func is None:
        special_mappings = {
            'html_preview': 'render_html_preview',
            'meirmaid': 'render_mermaid',
            'claudeCode_askQuestionTool': 'render_ask_question_tool'
        }
        for module_type, func_name in special_mappings.items():
            if module_name == module_type:
                render_func = getattr(module, func_name, None)
                break

    return render_func
```

Then update the endpoint to use this helper (replace the render_func lines in Step 1):

```python
# Chama função de renderização
render_func = _get_module_render_function(module, module_name)
visualization_html = ""
if render_func:
    visualization_html = render_func(content)
```

## Validation

Execute every command to validate patch is complete:

1. **Test server starts without errors:**
   ```bash
   python main.py
   ```
   Verify server starts on port 8000

2. **Test dynamic module loading for all 8 modules:**
   - Create test files for each module type in `projetos/test_project/`
   - Access `http://localhost:8000/api/modules/kanban?content=test` - should return HTML
   - Access `http://localhost:8000/api/modules/todolist?content=test` - should return HTML
   - Access `http://localhost:8000/api/modules/formulario?content=test` - should return HTML
   - Access `http://localhost:8000/api/modules/excalidraw?content=test` - should return HTML
   - Access `http://localhost:8000/api/modules/image_preview?content=test` - should return HTML

3. **Test frontend integration:**
   - Open `http://localhost:8000` in browser
   - Select a project with each module type
   - Verify visualization renders correctly (not just text fallback)
   - Verify user input renders correctly in sidebar

4. **Verify backward compatibility:**
   - Test that html_preview, meirmaid, and claudeCode_askQuestionTool still work
   - Test fallback mechanism if endpoint fails

## Patch Scope
- **Lines of code to change**: ~80 lines
- **Risk level**: Medium (modifies core rendering logic but keeps fallback)
- **Testing required**: Standard (test all 8 modules, verify backward compatibility)
