// API Base URL
const API_BASE = window.location.origin;

// State
let currentProject = null;
let currentFile = null;
let currentFileType = null;
let webhooksConfig = null;
let ws = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

async function initializeApp() {
    // Initialize Mermaid
    mermaid.initialize({
        startOnLoad: false,
        theme: 'default',
        securityLevel: 'loose'
    });

    // Load webhooks config
    await loadWebhooksConfig();

    // Load projects
    await loadProjects();

    // Setup event listeners
    setupEventListeners();

    // Connect WebSocket
    connectWebSocket();
}

function setupEventListeners() {
    // Project selector
    const projectSelector = document.getElementById('projectSelector');
    let lastSelectedValue = projectSelector.value;

    projectSelector.addEventListener('change', (e) => {
        const project = e.target.value;
        if (project && project !== lastSelectedValue) {
            lastSelectedValue = project;
            loadProjectFiles(project);
        }
    });

    // Add keyboard navigation support for project selector
    projectSelector.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            const selectedOption = projectSelector.options[projectSelector.selectedIndex];
            if (selectedOption && selectedOption.value) {
                // Only load if it's different from the last loaded project
                if (selectedOption.value !== lastSelectedValue) {
                    lastSelectedValue = selectedOption.value;
                    loadProjectFiles(selectedOption.value);
                }
            }
        }
    });

    // Reload button
    const reloadBtn = document.getElementById('reloadBtn');
    reloadBtn.addEventListener('click', () => {
        if (currentProject) {
            loadProjectFiles(currentProject);
        }
        showToast('Recarregado!', 'success');
    });

    // Configure webhook button
    const configureWebhookBtn = document.getElementById('configureWebhookBtn');
    configureWebhookBtn.addEventListener('click', () => {
        const newUrl = prompt('Insira a URL do webhook:', getCurrentWebhook());
        if (newUrl !== null) {
            updateWebhookUrl(newUrl);
        }
    });

    // Send button
    const sendBtn = document.getElementById('sendBtn');
    sendBtn.addEventListener('click', sendToWebhook);

    // Add keyboard navigation for file items
    document.addEventListener('keydown', (e) => {
        // Handle arrow keys for file navigation
        if (e.target.classList.contains('file-item')) {
            const fileItems = Array.from(document.querySelectorAll('.file-item'));
            const currentIndex = fileItems.indexOf(e.target);

            if (e.key === 'ArrowDown' && currentIndex < fileItems.length - 1) {
                e.preventDefault();
                fileItems[currentIndex + 1].focus();
                fileItems[currentIndex + 1].click();
            } else if (e.key === 'ArrowUp' && currentIndex > 0) {
                e.preventDefault();
                fileItems[currentIndex - 1].focus();
                fileItems[currentIndex - 1].click();
            }
        }
    });

    // Add Escape key to close loading overlay
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const loadingOverlay = document.getElementById('loadingOverlay');
            if (loadingOverlay && loadingOverlay.style.display !== 'none') {
                hideLoading();
            }
        }
    });
}

// API Calls
async function loadWebhooksConfig() {
    try {
        const response = await fetch(`${API_BASE}/api/webhooks/config`);
        webhooksConfig = await response.json();
        updateWebhookDisplay();
    } catch (error) {
        console.error('Error loading webhooks config:', error);
    }
}

async function loadProjects() {
    try {
        const response = await fetch(`${API_BASE}/api/projects`);
        const projects = await response.json();

        const selector = document.getElementById('projectSelector');
        selector.innerHTML = '<option value="">Selecione um projeto...</option>';

        projects.forEach(project => {
            const option = document.createElement('option');
            option.value = project.name;
            option.textContent = `${project.icon} ${project.display_name}`;
            selector.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading projects:', error);
        showToast('Erro ao carregar projetos', 'error');
    }
}

async function loadProjectFiles(projectName) {
    try {
        showLoading();

        const response = await fetch(`${API_BASE}/api/projects/${projectName}/files`);
        const files = await response.json();

        currentProject = projectName;

        // Display files in sidebar
        const filesList = document.getElementById('filesList');
        filesList.innerHTML = '';

        if (files.length === 0) {
            filesList.innerHTML = '<p class="text-muted" role="status">Nenhum arquivo encontrado</p>';
        } else {
            files.forEach((file, index) => {
                const fileItem = document.createElement('div');
                fileItem.className = 'file-item';
                fileItem.dataset.file = file.name;
                fileItem.setAttribute('role', 'button');
                fileItem.setAttribute('tabindex', '0');
                fileItem.setAttribute('aria-label', `Carregar arquivo ${file.name} do tipo ${file.type}`);
                fileItem.setAttribute('data-testid', `file-${index}`);

                fileItem.innerHTML = `
                    <span class="file-icon" aria-hidden="true">📄</span>
                    <span class="file-name">${file.name}</span>
                    <span class="file-badge">${file.type}</span>
                `;

                // Mouse click
                fileItem.addEventListener('click', () => loadFile(projectName, file.name));

                // Keyboard support
                fileItem.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        loadFile(projectName, file.name);
                    }
                });

                filesList.appendChild(fileItem);
            });
        }

        // Ensure #defaultInput exists in the sidebar
        ensureDefaultInputExists();

        // Update webhook display
        updateWebhookDisplay();

        hideLoading();
    } catch (error) {
        console.error('Error loading project files:', error);
        showToast('Erro ao carregar arquivos do projeto', 'error');
        hideLoading();
    }
}

function ensureDefaultInputExists() {
    const userInputContainer = document.getElementById('userInputContainer');
    const existingInput = document.getElementById('defaultInput');

    if (!existingInput) {
        // Preserve any existing input value
        const currentValue = userInputContainer.querySelector('textarea')?.value || '';
        userInputContainer.innerHTML = `
            <textarea id="defaultInput" class="user-input-textarea" placeholder="Digite seu input aqui...">${currentValue}</textarea>
        `;
    }
}

async function loadFile(projectName, fileName) {
    try {
        showLoading();

        const response = await fetch(`${API_BASE}/api/files/${projectName}/${fileName}`);
        const fileData = await response.json();

        currentFile = fileName;
        currentFileType = fileData.metadata;

        // Update file header
        document.getElementById('currentFileName').textContent = fileData.name;
        document.getElementById('fileType').textContent = fileData.metadata.module;
        document.getElementById('fileModified').textContent = new Date(fileData.metadata.modified * 1000).toLocaleString();

        // Update active file in sidebar
        document.querySelectorAll('.file-item').forEach(item => {
            item.classList.remove('active');
            if (item.dataset.file === fileName) {
                item.classList.add('active');
            }
        });

        // Enable send button
        document.getElementById('sendBtn').disabled = false;

        // Render content based on module
        await renderFileContent(fileData);

        // Render user input based on module
        renderUserInput(fileData);

        hideLoading();
    } catch (error) {
        console.error('Error loading file:', error);
        showToast('Erro ao carregar arquivo', 'error');
        hideLoading();
    }
}

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

function renderHTMLPreview(content, container) {
    container.innerHTML = `
        <div class="html-preview">
            <iframe id="htmlPreviewFrame" sandbox="allow-same-origin"></iframe>
        </div>
    `;

    const iframe = document.getElementById('htmlPreviewFrame');
    const doc = iframe.contentDocument || iframe.contentWindow.document;
    doc.open();
    doc.write(content);
    doc.close();
}

async function renderMermaidDiagram(content, container) {
    container.innerHTML = `
        <div class="mermaid-diagram">
            <pre class="mermaid">${content}</pre>
        </div>
    `;

    // Render Mermaid
    await mermaid.run();
}

function renderAskQuestionTool(content, container) {
    try {
        const data = JSON.parse(content);

        let html = '<div class="options-display">';
        html += `<h3>${data.question || 'Selecione as opções:'}</h3>`;
        html += '<div class="option-list">';

        if (data.options && Array.isArray(data.options)) {
            data.options.forEach(option => {
                const selected = option.selected ? 'selected' : '';
                html += `
                    <div class="option-item-display ${selected}">
                        <span>${option.selected ? '✓' : '○'}</span>
                        <span>${option.text || option.id}</span>
                    </div>
                `;
            });
        }

        html += '</div></div>';
        container.innerHTML = html;
    } catch (error) {
        console.error('Error parsing askQuestionTool:', error);
        renderTextContent(content, container);
    }
}

function renderTextContent(content, container) {
    container.innerHTML = `
        <div class="text-content">
            <pre style="white-space: pre-wrap; word-wrap: break-word;">${escapeHtml(content)}</pre>
        </div>
    `;
}

async function renderUserInput(fileData) {
    const container = document.getElementById('userInputContainer');
    const module = fileData.metadata.module;

    // Preserve existing input value if it exists
    const existingInput = document.getElementById('defaultInput');
    const preservedValue = existingInput ? existingInput.value : '';

    try {
        // Try dynamic module loading first
        const response = await fetch(`${API_BASE}/api/modules/${module}?content=${encodeURIComponent(fileData.content)}`);
        if (response.ok) {
            const moduleData = await response.json();
            if (moduleData.user_input_html) {
                container.innerHTML = moduleData.user_input_html;
                // Try to restore value if compatible
                const newInput = document.getElementById('defaultInput');
                if (newInput && preservedValue) {
                    newInput.value = preservedValue;
                }
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
            renderDefaultInput(container, preservedValue);
    }
}

function renderDefaultInput(container, preservedValue = '') {
    container.innerHTML = `
        <textarea id="defaultInput" class="user-input-textarea" placeholder="Digite seu input aqui...">${preservedValue}</textarea>
    `;
}

function renderAskQuestionToolInput(content, container) {
    try {
        const data = JSON.parse(content);

        let html = '<div class="options-input">';
        html += `<p style="margin-bottom: 0.75rem; font-size: 0.875rem;">${data.question || 'Selecione as opções:'}</p>`;

        if (data.options && Array.isArray(data.options)) {
            const inputType = data.allow_multiple ? 'checkbox' : 'radio';
            const inputName = 'askQuestionOptions';

            data.options.forEach(option => {
                html += `
                    <div class="option-item">
                        <input type="${inputType}" name="${inputName}" id="opt_${option.id}" value="${option.id}" ${option.selected ? 'checked' : ''}>
                        <label for="opt_${option.id}">${option.text || option.id}</label>
                    </div>
                `;
            });
        }

        html += '</div>';
        html += `<textarea id="userInputComment" class="user-input-textarea" placeholder="Adicione um comentário (opcional)..." style="margin-top: 0.75rem;"></textarea>`;

        container.innerHTML = html;
    } catch (error) {
        console.error('Error rendering askQuestionTool input:', error);
        renderDefaultInput(container);
    }
}

// WebSocket
function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        console.log('WebSocket connected');
        updateConnectionStatus('connected');
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        updateConnectionStatus('error');
    };

    ws.onclose = () => {
        console.log('WebSocket disconnected, reconnecting...');
        updateConnectionStatus('disconnected');
        setTimeout(connectWebSocket, 3000);
    };
}

// Connection Status Management
function updateConnectionStatus(status) {
    const statusIndicator = document.querySelector('.status-indicator');
    const statusText = document.getElementById('status-text');

    if (!statusIndicator || !statusText) return;

    // Remove all status classes
    statusIndicator.classList.remove('connected', 'error');

    switch (status) {
        case 'connected':
            statusIndicator.classList.add('connected');
            statusText.textContent = 'Conectado';
            break;
        case 'disconnected':
            statusText.textContent = 'Reconectando...';
            break;
        case 'error':
            statusIndicator.classList.add('error');
            statusText.textContent = 'Erro de conexão';
            break;
        default:
            statusText.textContent = 'Conectando...';
    }
}

async function handleWebSocketMessage(data) {
    if (data.type === 'file_updated') {
        // Check if it's the current file
        if (data.project === currentProject && data.file === currentFile) {
            // Update visualization only (preserve sidebar input)
            await renderFileContent({
                content: data.content,
                metadata: data.metadata
            });

            // Update file metadata
            document.getElementById('fileModified').textContent = new Date(data.timestamp).toLocaleString();

            showToast('Arquivo atualizado!', 'success');
        }
    }
}

// Subscribe to file updates
function subscribeToFile() {
    if (ws && ws.readyState === WebSocket.OPEN && currentProject && currentFile) {
        ws.send(JSON.stringify({
            type: 'subscribe',
            project: currentProject,
            file: currentFile
        }));
    }
}

// Send to Webhook
async function sendToWebhook() {
    if (!currentProject || !currentFile) {
        showToast('Selecione um arquivo primeiro', 'warning');
        return;
    }

    try {
        showLoading();

        const userInput = collectUserInput();

        const payload = {
            project: currentProject,
            file: currentFile,
            user_input: userInput
        };

        const response = await fetch(`${API_BASE}/api/send-webhook`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (result.success) {
            showToast('Enviado para webhook com sucesso!', 'success');

            // Add persistent success indicator for E2E testing
            const sendBtn = document.getElementById('sendBtn');
            const originalText = sendBtn.textContent;
            sendBtn.textContent = '✓ Enviado com Sucesso!';
            sendBtn.classList.add('success');
            sendBtn.disabled = true;

            // Reset button after 5 seconds
            setTimeout(() => {
                sendBtn.textContent = originalText;
                sendBtn.classList.remove('success');
                sendBtn.disabled = false;
            }, 5000);

            // Subscribe to updates for this file
            subscribeToFile();
        } else {
            showToast(`Erro ao enviar: ${result.error || 'Erro desconhecido'}`, 'error');
        }

        hideLoading();
    } catch (error) {
        console.error('Error sending to webhook:', error);
        showToast('Erro ao enviar para webhook', 'error');
        hideLoading();
    }
}

function collectUserInput() {
    const module = currentFileType?.module;

    switch (module) {
        case 'claudeCode_askQuestionTool':
            return collectAskQuestionToolInput();
        default:
            return {
                type: 'text',
                data: document.getElementById('defaultInput')?.value || ''
            };
    }
}

function collectAskQuestionToolInput() {
    const checkedInputs = document.querySelectorAll('input[name="askQuestionOptions"]:checked');
    const selectedOptions = Array.from(checkedInputs).map(input => input.value);
    const comment = document.getElementById('userInputComment')?.value || '';

    return {
        type: 'options',
        data: {
            selected: selectedOptions,
            comment: comment
        }
    };
}

// Webhook Helpers
function getCurrentWebhook() {
    if (!webhooksConfig) return '';

    // Try project specific webhook
    if (currentProject && webhooksConfig.projects && webhooksConfig.projects[currentProject]) {
        const projectConfig = webhooksConfig.projects[currentProject];
        if (projectConfig.webhook) {
            return projectConfig.webhook;
        }
    }

    // Fallback to global webhook
    return webhooksConfig.global?.default_webhook || '';
}

function updateWebhookDisplay() {
    const webhookUrl = getCurrentWebhook();
    document.getElementById('webhookUrl').textContent = webhookUrl || 'Não configurado';
}

function updateWebhookUrl(newUrl) {
    // This would update the webhooks.json file
    // For now, just show a message
    showToast('URL do webhook atualizada (não persistida)', 'success');
    document.getElementById('webhookUrl').textContent = newUrl;
}

// Utility Functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showLoading() {
    document.getElementById('loadingOverlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;

    // Clear any existing timeout
    if (toast.timeoutId) {
        clearTimeout(toast.timeoutId);
    }

    // Set new timeout and store the ID
    toast.timeoutId = setTimeout(() => {
        toast.classList.remove('show');
    }, 5000);
}

// Auto-subscribe when file changes
const originalLoadFile = loadFile;
loadFile = async function(projectName, fileName) {
    await originalLoadFile(projectName, fileName);
    subscribeToFile();
};
