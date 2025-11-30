// Use relative path for production (Vercel), or fallback to localhost for development
const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
    ? 'http://127.0.0.1:8000/api/tasks' 
    : '/api/tasks';

// DOM Elements
const jsonInput = document.getElementById('task-json');
const analyzeBtn = document.getElementById('analyze-btn');
const suggestBtn = document.getElementById('suggest-btn');
const taskList = document.getElementById('task-list');
const errorMsg = document.getElementById('error-msg');
const loading = document.getElementById('loading');
const tabBtns = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');
const strategySelect = document.getElementById('strategy-select');

// Manual Form Elements
const addTaskBtn = document.getElementById('add-task-btn');
const manualListPreview = document.getElementById('manual-list-preview');
let manualTasks = [];

// Event Listeners
tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        tabBtns.forEach(b => b.classList.remove('active'));
        tabContents.forEach(c => c.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById(btn.dataset.tab).classList.add('active');
    });
});

addTaskBtn.addEventListener('click', () => {
    const title = document.getElementById('t-title').value;
    const due = document.getElementById('t-due').value;
    const hours = document.getElementById('t-hours').value;
    const imp = document.getElementById('t-imp').value;
    const deps = document.getElementById('t-deps').value;

    if (!title || !due || !hours) {
        alert("Please fill in required fields");
        return;
    }

    const newTask = {
        id: manualTasks.length + 100, // Temp ID for manual
        title,
        due_date: due,
        estimated_hours: parseFloat(hours),
        importance: parseInt(imp),
        dependencies: deps ? deps.split(',').map(d => parseInt(d.trim())).filter(n => !isNaN(n)) : []
    };

    manualTasks.push(newTask);
    updateManualPreview();
    document.getElementById('task-form').reset();
});

analyzeBtn.addEventListener('click', async () => {
    let tasks = [];
    const activeTab = document.querySelector('.tab-btn.active').dataset.tab;

    if (activeTab === 'json-input') {
        try {
            tasks = JSON.parse(jsonInput.value);
        } catch (e) {
            showError("Invalid JSON format");
            return;
        }
    } else {
        tasks = manualTasks;
    }

    if (tasks.length === 0) {
        showError("No tasks to analyze");
        return;
    }

    await analyzeTasks(tasks);
});

suggestBtn.addEventListener('click', async () => {
    setLoading(true);
    try {
        const res = await fetch(`${API_URL}/suggest/`);
        if (!res.ok) throw new Error('Failed to fetch suggestions (Database might be empty/reset)');
        const data = await res.json();
        renderTasks(data);
    } catch (err) {
        showError(err.message);
    } finally {
        setLoading(false);
    }
});

// Functions
function updateManualPreview() {
    manualListPreview.innerHTML = manualTasks.map(t =>
        `<div style="padding: 0.5rem; background: #334155; margin-top: 0.5rem; border-radius: 4px;">
            #${t.id} ${t.title} (Due: ${t.due_date})
        </div>`
    ).join('');
}

async function analyzeTasks(tasks) {
    setLoading(true);
    errorMsg.classList.add('hidden');
    taskList.innerHTML = '';

    const useAi = document.getElementById('use-ai-check').checked;
    const strategy = strategySelect.value;
    
    // Construct Query Params
    const params = new URLSearchParams({
        use_ai: useAi,
        strategy: strategy
    });

    const url = `${API_URL}/analyze/?${params.toString()}`;

    try {
        const res = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(tasks)
        });

        const data = await res.json();

        if (!res.ok) {
            if (data.details) {
                if (Array.isArray(data.details)) {
                    throw new Error(data.error + ": " + data.details.join(', '));
                }
            }
            throw new Error(data.error || JSON.stringify(data));
        }

        renderTasks(data);
    } catch (err) {
        showError(err.message);
    } finally {
        setLoading(false);
    }
}

function renderTasks(tasks) {
    if (tasks.length === 0) {
        taskList.innerHTML = '<p style="text-align:center; color:#94a3b8;">No tasks found.</p>';
        return;
    }
    
    taskList.innerHTML = tasks.map(task => {
        let priorityClass = 'priority-low';
        if (task.score >= 80) priorityClass = 'priority-high';
        else if (task.score >= 50) priorityClass = 'priority-med';

        return `
            <div class="task-card">
                <div class="task-info">
                    <h3>${task.title} <span style="font-size:0.8em; color:#94a3b8;">(#${task.id})</span></h3>
                    <div class="task-meta">
                        Due: ${task.due_date} | Est: ${task.estimated_hours}h | Imp: ${task.importance}/10
                    </div>
                    <div class="explanation">
                        💡 ${task.explanation}
                    </div>
                </div>
                <div class="score-badge ${priorityClass}">
                    ${Math.round(task.score)}
                </div>
            </div>
        `;
    }).join('');
}

function showError(msg) {
    errorMsg.textContent = msg;
    errorMsg.classList.remove('hidden');
}

function setLoading(isLoading) {
    if (isLoading) {
        loading.classList.remove('hidden');
        taskList.classList.add('hidden');
    } else {
        loading.classList.add('hidden');
        taskList.classList.remove('hidden');
    }
}