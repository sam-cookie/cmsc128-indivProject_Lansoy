import { sortTasks } from './taskSort.js';

export function initializeTaskEdit() {
    // Module is initialized through exported functions
}

export function openEditModal(taskDiv, taskId, isCollabTask) {
    const taskNameDiv = taskDiv.querySelector('.task-name');
    const taskDateDiv = taskDiv.querySelector('.task-date');
    const taskTimeDiv = taskDiv.querySelector('.task-time');
    const oldDate = taskDateDiv.textContent.trim();
    const oldTime = taskTimeDiv.textContent.trim().replace('🕐 ', '');

    const editForm = document.createElement('form');
    editForm.className = 'edit-overlay';

    // Create form header
    const formHeader = document.createElement('div');
    formHeader.style.cssText = 'display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;';
    formHeader.innerHTML = '<i class="fa-solid fa-edit"></i><h3 style="margin: 0; color: var(--text-primary);">Edit Task</h3>';
    editForm.appendChild(formHeader);

    const editTaskInput = document.createElement('input');
    editTaskInput.type = 'text';
    editTaskInput.value = taskNameDiv.textContent;
    editTaskInput.placeholder = 'Task name';
    editTaskInput.required = true;

    const editPrioritySelect = document.createElement('select');
    editPrioritySelect.innerHTML = `
        <option value="high" style="background: #B45253; color: white;">High Priority</option>
        <option value="mid" style="background: #FCB53B; color: black;">Medium Priority</option>
        <option value="low" style="background: #84994F; color: white;">Low Priority</option>
    `;
    ['high', 'mid', 'low'].forEach(optionVal => {
        if (taskDiv.classList.contains(optionVal)) {
            editPrioritySelect.value = optionVal;
        }
    });

    const editDateInput = document.createElement('input');
    editDateInput.type = 'date';
    editDateInput.value = oldDate;

    const editTimeInput = document.createElement('input');
    editTimeInput.type = 'time';
    editTimeInput.value = oldTime;

    const buttonContainer = document.createElement('div');
    buttonContainer.style.cssText = 'display: flex; gap: 0.75rem; margin-top: 0.5rem;';

    const saveBtn = document.createElement('button');
    saveBtn.type = 'submit';
    saveBtn.innerHTML = '<i class="fa-solid fa-check"></i> Save';

    const cancelBtn = document.createElement('button');
    cancelBtn.type = 'button';
    cancelBtn.innerHTML = '<i class="fa-solid fa-times"></i> Cancel';

    buttonContainer.appendChild(saveBtn);
    buttonContainer.appendChild(cancelBtn);

    editForm.appendChild(editTaskInput);
    editForm.appendChild(editPrioritySelect);
    editForm.appendChild(editDateInput);
    editForm.appendChild(editTimeInput);
    editForm.appendChild(buttonContainer);

    // Add backdrop for emphasis
    const backdrop = document.createElement('div');
    backdrop.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        z-index: 9998;
        backdrop-filter: blur(4px);
    `;

    document.body.appendChild(backdrop);
    document.body.appendChild(editForm);
    editForm.style.display = "flex"; 
    editTaskInput.focus();

    const closeModal = () => {
        editForm.remove();
        backdrop.remove();
    };

    cancelBtn.addEventListener('click', function(e) {
        e.preventDefault();
        closeModal();
    });

    backdrop.addEventListener('click', closeModal);

    // Keyboard shortcuts
    editForm.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeModal();
        }
    });

    editForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (!editTaskInput.value.trim()) {
            editTaskInput.style.animation = 'shake 0.5s ease-in-out';
            editTaskInput.focus();
            return;
        }

        saveBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Saving...';
        saveBtn.disabled = true;

        // Determine the endpoint based on context
        const endpoint = isCollabTask ? `/edit_collab_task/${taskId}` : `/edit_task/${taskId}`;

        fetch(endpoint, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: editTaskInput.value.trim(),
                date: editDateInput.value,
                time: editTimeInput.value,
                priority: editPrioritySelect.value
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                taskNameDiv.textContent = editTaskInput.value.trim();
                taskDateDiv.textContent = editDateInput.value;
                taskTimeDiv.innerHTML = `<i class="fa-solid fa-clock"></i> ${editTimeInput.value}`;
                
                // updating priority badges
                const priorityBadge = taskDiv.querySelector('.task-priority-badge');
                priorityBadge.textContent = editPrioritySelect.value.charAt(0).toUpperCase() + editPrioritySelect.value.slice(1);
                priorityBadge.className = `task-priority-badge ${editPrioritySelect.value}`;
                
                taskDiv.classList.remove('high', 'mid', 'low');
                taskDiv.classList.add(editPrioritySelect.value);
                closeModal();
                
                if (!isCollabTask) {
                    sortTasks(); 
                }
            }
        })
        .catch(error => {
            console.error('Error updating task:', error);
            saveBtn.innerHTML = '<i class="fa-solid fa-exclamation-triangle"></i> Error';
            setTimeout(() => {
                saveBtn.innerHTML = '<i class="fa-solid fa-check"></i> Save';
                saveBtn.disabled = false;
            }, 2000);
        });
    });
}