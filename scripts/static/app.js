// State Management
let currentLogs = [];
let traces = [];

// DOM Elements
const logTerminal = document.getElementById('log-terminal');
const tracesTable = document.querySelector('#recent-traces-table tbody');
const newJobBtn = document.getElementById('new-job-btn');
const jobModal = document.getElementById('job-modal');
const runBtn = document.getElementById('run-btn');
const cancelBtn = document.getElementById('cancel-btn');
const taskInput = document.getElementById('task-input');

// API Calls
async function fetchLogs() {
    try {
        const response = await fetch('/api/logs');
        const data = await response.json();
        updateLogs(data.logs);
    } catch (err) {
        console.error('Failed to fetch logs:', err);
    }
}

async function fetchTraces() {
    try {
        const response = await fetch('/api/traces');
        const data = await response.json();
        updateTraces(data.traces);
    } catch (err) {
        console.error('Failed to fetch traces:', err);
    }
}

async function runJob(task) {
    try {
        setPipelineState('plan', 'active');
        const response = await fetch('/api/jobs', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task })
        });
        const data = await response.json();
        addLog(`Job created: ${data.manifest.task}`, 'system');
        
        // Start polling for logs and state
        startPolling();
    } catch (err) {
        addLog(`Error: ${err.message}`, 'error');
    }
}

// UI Updates
function updateLogs(logs) {
    if (logs.length === currentLogs.length) return;
    
    // Clear and re-render logs for simplicity
    logTerminal.innerHTML = '';
    logs.forEach(log => {
        const div = document.createElement('div');
        div.className = 'line';
        if (log.includes('started')) div.classList.add('system');
        if (log.includes('Error')) div.classList.add('error');
        div.textContent = `> ${log}`;
        logTerminal.appendChild(div);
    });
    logTerminal.scrollTop = logTerminal.scrollHeight;
    currentLogs = logs;

    // Auto-update pipeline state based on log content
    if (logs.some(l => l.includes('generated'))) setPipelineState('plan', 'complete');
    if (logs.some(l => l.includes('execution started'))) {
        setPipelineState('build', 'complete');
        setPipelineState('run', 'active');
    }
    if (logs.some(l => l.includes('completed'))) {
        setPipelineState('run', 'complete');
    }
}

function updateTraces(newTraces) {
    tracesTable.innerHTML = '';
    newTraces.forEach(trace => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td style="font-family: monospace;">${trace.trace_id.substring(0, 8)}...</td>
            <td><span class="status-pill ${trace.status.toLowerCase()}">${trace.status}</span></td>
            <td>${trace.duration_ms}ms</td>
            <td>${new Date(trace.start_time).toLocaleTimeString()}</td>
        `;
        tracesTable.appendChild(row);
    });
}

function setPipelineState(stepId, state) {
    const step = document.getElementById(`step-${stepId}`);
    step.classList.remove('active', 'complete');
    if (state) step.classList.add(state);
}

function addLog(text, type) {
    const div = document.createElement('div');
    div.className = `line ${type || ''}`;
    div.textContent = `> ${text}`;
    logTerminal.appendChild(div);
    logTerminal.scrollTop = logTerminal.scrollHeight;
}

// Event Listeners
newJobBtn.onclick = () => jobModal.classList.remove('hidden');
cancelBtn.onclick = () => jobModal.classList.add('hidden');

runBtn.onclick = () => {
    const task = taskInput.value.trim();
    if (task) {
        runJob(task);
        jobModal.classList.add('hidden');
        taskInput.value = '';
    }
};

// Polling
let pollInterval;
function startPolling() {
    if (pollInterval) clearInterval(pollInterval);
    pollInterval = setInterval(() => {
        fetchLogs();
        fetchTraces();
    }, 2000);
}

// Initial Load
fetchTraces();
setInterval(fetchTraces, 5000);
startPolling();

// Add some basic styling for pills
const style = document.createElement('style');
style.textContent = `
    .status-pill {
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
    }
    .status-pill.ok { background: rgba(16, 185, 129, 0.2); color: #10b981; }
    .status-pill.error { background: rgba(239, 68, 68, 0.2); color: #ef4444; }
`;
document.head.appendChild(style);
