const state = {
    agents: [],
    teams: [],
    workflows: [],
    activeResource: null,
    sessionId: null
};

// UI Elements
const el = {
    agentList: document.getElementById('agent-list'),
    teamList: document.getElementById('team-list'),
    workflowList: document.getElementById('workflow-list'),
    chatContainer: document.getElementById('chat-container'),
    chatInput: document.getElementById('chat-input'),
    sendBtn: document.getElementById('send-btn'),
    activeName: document.getElementById('active-name'),
    activeDesc: document.getElementById('active-description'),
    statusDot: document.getElementById('connection-dot'),
    statusText: document.getElementById('status-text'),
    statAgents: document.getElementById('stat-agents'),
    statTeams: document.getElementById('stat-teams'),
    statWorkflows: document.getElementById('stat-workflows'),
    clearBtn: document.getElementById('clear-chat')
};

// --- Initialization ---

async function init() {
    try {
        await Promise.all([
            fetchInfo(),
            fetchResources('agents'),
            fetchResources('teams'),
            fetchResources('workflows')
        ]);
        
        el.statusDot.className = 'dot online';
        el.statusText.innerText = 'Connected';
    } catch (error) {
        console.error('Failed to initialize AgentOS:', error);
        el.statusText.innerText = 'Error Connecting';
    }
}

// --- Data Fetching ---

async function fetchInfo() {
    const res = await fetch('/info');
    const data = await res.json();
    el.statAgents.innerText = data.agent_count;
    el.statTeams.innerText = data.team_count;
    el.statWorkflows.innerText = data.workflow_count;
}

async function fetchResources(type) {
    const res = await fetch('/' + type);
    const data = await res.json();
    state[type] = data;
    renderList(type, data);
}

function renderList(type, items) {
    const listEl = el[type.slice(0, -1) + 'List'];
    listEl.innerHTML = '';
    
    items.forEach(item => {
        const li = document.createElement('li');
        li.className = 'resource-item';
        li.innerText = item.name || item.id;
        li.onclick = () => selectResource(type, item);
        listEl.appendChild(li);
    });
}

function selectResource(type, item) {
    state.activeResource = { type, ...item };
    state.sessionId = null; // New session for new resource selection
    
    // Update UI
    document.querySelectorAll('.resource-item').forEach(li => li.classList.remove('active'));
    event.target.classList.add('active');
    
    el.activeName.innerText = item.name || item.id;
    el.activeDesc.innerText = item.description || `Interacting with ${type.slice(0, -1)}`;
    el.chatInput.disabled = false;
    el.sendBtn.disabled = false;
    
    // Clear chat area except for a welcome message
    el.chatContainer.innerHTML = '';
    addMessage('agent', `Hello! I am ${item.name || item.id}. How can I help you today?`);
}

// --- Chat Logic ---

async function sendMessage() {
    const message = el.chatInput.value.trim();
    if (!message || !state.activeResource) return;
    
    el.chatInput.value = '';
    el.chatInput.style.height = 'auto';
    addMessage('user', message);
    
    const agentMsgEl = addMessage('agent', '...');
    const contentEl = agentMsgEl.querySelector('.content') || agentMsgEl;
    contentEl.innerText = '';

    try {
        const formData = new FormData();
        formData.append('message', message);
        formData.append('stream', 'true');
        if (state.sessionId) formData.append('session_id', state.sessionId);

        const resourceType = state.activeResource.type; // agents, teams, workflows
        const resourceId = state.activeResource.id;

        const response = await fetch(`/${resourceType}/${resourceId}/runs`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error('Failed to send message');

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop();

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const data = JSON.parse(line.slice(6));
                        
                        if (data.session_id) state.sessionId = data.session_id;
                        
                        // Agno sends various events. We look for 'content' or 'RunResponse'
                        if (data.content !== undefined) {
                            contentEl.innerText += data.content;
                        } else if (data.event === 'RunResponse' && data.data && data.data.content) {
                             contentEl.innerText += data.data.content;
                        }
                        
                        // Scroll to bottom
                        el.chatContainer.scrollTop = el.chatContainer.scrollHeight;
                    } catch (e) {
                        // Not partial JSON or different event
                    }
                }
            }
        }
    } catch (error) {
        console.error('Chat error:', error);
        contentEl.innerText = 'Error: ' + error.message;
    }
}

function addMessage(sender, text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}-message`;
    msgDiv.innerText = text;
    el.chatContainer.appendChild(msgDiv);
    el.chatContainer.scrollTop = el.chatContainer.scrollHeight;
    return msgDiv;
}

// --- Event Listeners ---

el.sendBtn.onclick = sendMessage;
el.chatInput.onkeydown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
};

el.chatInput.oninput = () => {
    el.chatInput.style.height = 'auto';
    el.chatInput.style.height = el.chatInput.scrollHeight + 'px';
};

el.clearBtn.onclick = () => {
    el.chatContainer.innerHTML = '';
    if (state.activeResource) {
        addMessage('agent', `Chat cleared. How can I help you?`);
    }
};

// Initialize
init();
