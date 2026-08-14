/**
 * TaskFlow Pro — Frontend REST API Client Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    // API Endpoints
    const API_BASE = '/tasks';
    const HEALTH_URL = '/health';

    // State Management
    let allTasks = [];
    let activeStatusFilter = 'all'; // 'all', 'active', 'completed'
    let activePriorityFilter = 'all'; // 'all', 'high', 'medium', 'low'
    let searchQuery = '';
    let sortMode = 'newest'; // 'newest', 'oldest', 'priority'

    // DOM Element Selections
    const taskList = document.getElementById('taskList');
    const searchInput = document.getElementById('searchInput');
    const sortSelect = document.getElementById('sortSelect');
    const sectionTitle = document.getElementById('sectionTitle');

    // Metrics Elements
    const metricTotal = document.getElementById('metricTotal');
    const metricPending = document.getElementById('metricPending');
    const metricRate = document.getElementById('metricRate');
    const metricHigh = document.getElementById('metricHigh');
    
    // Sidebar Counts
    const countAll = document.getElementById('countAll');
    const countActive = document.getElementById('countActive');
    const countCompleted = document.getElementById('countCompleted');

    // Health Card Elements
    const statusIndicator = document.getElementById('statusIndicator');
    const statusValue = document.getElementById('statusValue');
    const refreshHealthBtn = document.getElementById('refreshHealthBtn');

    // Modal Elements
    const createModal = document.getElementById('createModal');
    const editModal = document.getElementById('editModal');
    const openCreateModalBtn = document.getElementById('openCreateModalBtn');
    const closeCreateModalBtn = document.getElementById('closeCreateModalBtn');
    const cancelCreateBtn = document.getElementById('cancelCreateBtn');
    const createTaskForm = document.getElementById('createTaskForm');
    
    const closeEditModalBtn = document.getElementById('closeEditModalBtn');
    const cancelEditBtn = document.getElementById('cancelEditBtn');
    const editTaskForm = document.getElementById('editTaskForm');

    // --- Toast Notifications ---
    function showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        let icon = 'fa-info-circle';
        if (type === 'success') icon = 'fa-check-circle';
        if (type === 'error') icon = 'fa-exclamation-circle';

        toast.innerHTML = `
            <i class="fa-solid ${icon}"></i>
            <span>${escapeHtml(message)}</span>
        `;

        container.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(10px)';
            setTimeout(() => toast.remove(), 300);
        }, 3500);
    }

    // --- Helper Utility: XSS Escaping ---
    function escapeHtml(text) {
        if (!text) return '';
        return text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    // --- API Interactions ---

    // 1. Fetch System Health
    async function checkHealth() {
        try {
            statusValue.textContent = 'Checking...';
            const res = await fetch(HEALTH_URL);
            if (res.ok) {
                const data = await res.json();
                statusIndicator.className = 'status-indicator online';
                statusValue.textContent = `${data.repository_type.toUpperCase()} Healthy`;
            } else {
                throw new Error(`HTTP ${res.status}`);
            }
        } catch (err) {
            statusIndicator.className = 'status-indicator offline';
            statusValue.textContent = 'System Error';
        }
    }

    // 2. Fetch Tasks List from REST API (GET /tasks)
    async function loadTasks() {
        try {
            const res = await fetch(`${API_BASE}?limit=500`);
            if (!res.ok) throw new Error('Failed to fetch tasks from server');
            allTasks = await res.json();
            renderApp();
        } catch (err) {
            taskList.innerHTML = `
                <div class="empty-state">
                    <i class="fa-solid fa-triangle-exclamation" style="color: var(--color-danger)"></i>
                    <h3>Error Loading Tasks</h3>
                    <p>${escapeHtml(err.message)}</p>
                </div>
            `;
            showToast(err.message, 'error');
        }
    }

    // 3. Create Task (POST /tasks)
    createTaskForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const title = document.getElementById('createTitle').value.trim();
        const description = document.getElementById('createDescription').value.trim();
        const priority = document.getElementById('createPriority').value;

        if (!title) {
            showToast('Task title is required', 'error');
            return;
        }

        try {
            const res = await fetch(API_BASE, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, description, priority })
            });

            if (!res.ok) {
                const errData = await res.json();
                throw new Error(errData.message || 'Failed to create task');
            }

            const newTask = await res.json();
            allTasks.unshift(newTask);
            closeModal(createModal);
            createTaskForm.reset();
            renderApp();
            showToast('Task created successfully!', 'success');
        } catch (err) {
            showToast(err.message, 'error');
        }
    });

    // 4. Toggle Task Completion (PUT /tasks/{id})
    async function toggleTaskCompleted(taskId, newStatus) {
        const task = allTasks.find(t => t.id === taskId);
        if (!task) return;

        const previousStatus = task.completed;
        task.completed = newStatus; // Optimistic UI update
        renderApp();

        try {
            const res = await fetch(`${API_BASE}/${taskId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ completed: newStatus })
            });

            if (!res.ok) {
                task.completed = previousStatus; // Rollback
                renderApp();
                throw new Error('Failed to update task completion');
            }

            const updatedTask = await res.json();
            Object.assign(task, updatedTask);
            renderApp();
            showToast(`Task marked as ${newStatus ? 'completed' : 'active'}`, 'info');
        } catch (err) {
            showToast(err.message, 'error');
        }
    }

    // 5. Update Task Details (PUT /tasks/{id})
    editTaskForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const taskId = document.getElementById('editTaskId').value;
        const title = document.getElementById('editTitle').value.trim();
        const description = document.getElementById('editDescription').value.trim();
        const priority = document.getElementById('editPriority').value;
        const completed = document.getElementById('editCompleted').value === 'true';

        try {
            const res = await fetch(`${API_BASE}/${taskId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, description, priority, completed })
            });

            if (!res.ok) {
                const errData = await res.json();
                throw new Error(errData.message || 'Failed to update task');
            }

            const updatedTask = await res.json();
            const index = allTasks.findIndex(t => t.id === taskId);
            if (index !== -1) {
                allTasks[index] = updatedTask;
            }

            closeModal(editModal);
            renderApp();
            showToast('Task updated successfully!', 'success');
        } catch (err) {
            showToast(err.message, 'error');
        }
    });

    // 6. Delete Task (DELETE /tasks/{id})
    async function deleteTask(taskId) {
        if (!confirm('Are you sure you want to delete this task?')) return;

        try {
            const res = await fetch(`${API_BASE}/${taskId}`, { method: 'DELETE' });
            if (!res.ok && res.status !== 204) {
                throw new Error('Failed to delete task');
            }

            allTasks = allTasks.filter(t => t.id !== taskId);
            renderApp();
            showToast('Task deleted successfully', 'info');
        } catch (err) {
            showToast(err.message, 'error');
        }
    }

    // --- Rendering Engine ---
    function renderApp() {
        updateMetrics();
        renderTaskList();
    }

    function updateMetrics() {
        const total = allTasks.length;
        const active = allTasks.filter(t => !t.completed).length;
        const completed = allTasks.filter(t => t.completed).length;
        const highPriority = allTasks.filter(t => t.priority === 'high' && !t.completed).length;
        
        const rate = total > 0 ? Math.round((completed / total) * 100) : 0;

        metricTotal.textContent = total;
        metricPending.textContent = active;
        metricRate.textContent = `${rate}%`;
        metricHigh.textContent = highPriority;

        countAll.textContent = total;
        countActive.textContent = active;
        countCompleted.textContent = completed;
    }

    function renderTaskList() {
        // Filter tasks
        let filtered = allTasks.filter(task => {
            // Status filter
            if (activeStatusFilter === 'active' && task.completed) return false;
            if (activeStatusFilter === 'completed' && !task.completed) return false;
            
            // Priority filter
            if (activePriorityFilter !== 'all' && task.priority !== activePriorityFilter) return false;

            // Search query
            if (searchQuery) {
                const query = searchQuery.toLowerCase();
                const matchTitle = task.title.toLowerCase().includes(query);
                const matchDesc = (task.description || '').toLowerCase().includes(query);
                return matchTitle || matchDesc;
            }

            return true;
        });

        // Sort tasks
        filtered.sort((a, b) => {
            if (sortMode === 'newest') return new Date(b.created_at) - new Date(a.created_at);
            if (sortMode === 'oldest') return new Date(a.created_at) - new Date(b.created_at);
            if (sortMode === 'priority') {
                const pMap = { high: 3, medium: 2, low: 1 };
                return pMap[b.priority] - pMap[a.priority];
            }
            return 0;
        });

        if (filtered.length === 0) {
            taskList.innerHTML = `
                <div class="empty-state">
                    <i class="fa-solid fa-clipboard-list"></i>
                    <h3>No tasks found</h3>
                    <p>Try adjusting your search criteria or create a new task!</p>
                </div>
            `;
            return;
        }

        taskList.innerHTML = filtered.map(task => {
            const formattedDate = new Date(task.created_at).toLocaleDateString(undefined, {
                month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
            });

            return `
                <div class="task-item ${task.completed ? 'completed-item' : ''}" data-id="${task.id}">
                    <input type="checkbox" class="task-checkbox" ${task.completed ? 'checked' : ''} data-action="toggle">
                    
                    <div class="task-content">
                        <span class="task-title">${escapeHtml(task.title)}</span>
                        ${task.description ? `<span class="task-description">${escapeHtml(task.description)}</span>` : ''}
                        
                        <div class="task-meta">
                            <span class="badge-priority ${task.priority}">${task.priority}</span>
                            <span><i class="fa-regular fa-clock"></i> ${formattedDate}</span>
                        </div>
                    </div>

                    <div class="task-actions">
                        <button class="action-btn edit-btn" data-action="edit" title="Edit Task">
                            <i class="fa-solid fa-pen"></i>
                        </button>
                        <button class="action-btn delete-btn" data-action="delete" title="Delete Task">
                            <i class="fa-solid fa-trash-can"></i>
                        </button>
                    </div>
                </div>
            `;
        }).join('');
    }

    // --- Event Delegations & Listeners ---

    // Task Item Event Delegation (Check, Edit, Delete)
    taskList.addEventListener('click', (e) => {
        const taskItem = e.target.closest('.task-item');
        if (!taskItem) return;
        const taskId = taskItem.dataset.id;

        const actionTarget = e.target.closest('[data-action]');
        if (!actionTarget) return;

        const action = actionTarget.dataset.action;

        if (action === 'toggle') {
            toggleTaskCompleted(taskId, actionTarget.checked);
        } else if (action === 'delete') {
            deleteTask(taskId);
        } else if (action === 'edit') {
            openEditModal(taskId);
        }
    });

    // Edit Modal Opener
    function openEditModal(taskId) {
        const task = allTasks.find(t => t.id === taskId);
        if (!task) return;

        document.getElementById('editTaskId').value = task.id;
        document.getElementById('editTitle').value = task.title;
        document.getElementById('editDescription').value = task.description || '';
        document.getElementById('editPriority').value = task.priority;
        document.getElementById('editCompleted').value = task.completed ? 'true' : 'false';

        openModal(editModal);
    }

    // Status Filter Nav
    document.querySelectorAll('.nav-item').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            activeStatusFilter = btn.dataset.filterStatus;
            
            sectionTitle.textContent = btn.innerText.split('\n')[0].trim();
            renderTaskList();
        });
    });

    // Priority Filter Buttons
    document.querySelectorAll('.priority-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.priority-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            activePriorityFilter = btn.dataset.priority;
            renderTaskList();
        });
    });

    // Search Input Listener
    searchInput.addEventListener('input', (e) => {
        searchQuery = e.target.value.trim();
        renderTaskList();
    });

    // Sort Selector Listener
    sortSelect.addEventListener('change', (e) => {
        sortMode = e.target.value;
        renderTaskList();
    });

    // Refresh Health Check Button
    refreshHealthBtn.addEventListener('click', checkHealth);

    // Modal Visibility Helpers
    function openModal(modal) {
        modal.classList.add('active');
    }

    function closeModal(modal) {
        modal.classList.remove('active');
    }

    openCreateModalBtn.addEventListener('click', () => openModal(createModal));
    closeCreateModalBtn.addEventListener('click', () => closeModal(createModal));
    cancelCreateBtn.addEventListener('click', () => closeModal(createModal));
    
    closeEditModalBtn.addEventListener('click', () => closeModal(editModal));
    cancelEditBtn.addEventListener('click', () => closeModal(editModal));

    // Close Modals on Overlay Backdrop Click
    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal-overlay')) {
            closeModal(createModal);
            closeModal(editModal);
        }
    });

    // Initialize Application Data
    checkHealth();
    loadTasks();
});
