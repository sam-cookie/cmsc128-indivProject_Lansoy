import { createTaskElement } from './taskEvents.js';
import { sortTasks } from './taskSort.js';

export function initializeTaskCreation() {
    const addTaskBtn = document.getElementById('add-task-button');
    const taskInput = document.getElementById('task-input');
    const prioritySelect = document.getElementById('priority-select');
    const timeInput = document.getElementById('time-input');
    const dateInput = document.getElementById('date-input');

    const isCollaboration = document.querySelector('[data-collab="true"]') || 
                           document.getElementById('collab-list-id');
    const LIST_ID = isCollaboration ? document.getElementById('collab-list-id')?.value : null;

    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            addTaskBtn?.click();
        }
        
        if (e.key === 'Escape' && document.activeElement === taskInput) {
            taskInput.value = '';
            taskInput.blur();
        }
    });

    taskInput?.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            addTaskBtn?.click();
        }
    });

    taskInput?.addEventListener('focus', function() {
        taskInput.style.transform = 'scale(1.02)';
    });

    taskInput?.addEventListener('blur', function() {
        taskInput.style.transform = 'scale(1)';
    });

    // Add shake animation for empty input
    const style = document.createElement('style');
    style.textContent = `
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-5px); }
            75% { transform: translateX(5px); }
        }
    `;
    document.head.appendChild(style);

    addTaskBtn?.addEventListener('click', handleAddTask);

    function handleAddTask() {
        const taskText = taskInput.value.trim();
        const priority = prioritySelect.value;
        const date = dateInput.value;
        const time = timeInput.value;

        if (taskText !== '') {
            // Add loading state
            addTaskBtn.classList.add('loading');
            addTaskBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Adding...';
            
            // Determine the endpoint based on context
            const endpoint = isCollaboration ? `/add_collab_task/${LIST_ID}` : '/add_task';
            
            fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: taskText,
                    priority: priority,
                    date: date,
                    time: time
                })
            })
            .then(res => res.json())
            .then(task => {
                addTaskBtn.innerHTML = '<i class="fa-solid fa-check"></i> Added!';
                addTaskBtn.style.background = 'linear-gradient(135deg, #10b981, #059669)';
                
                const taskElement = createTaskElement(task);
                
                let backlogContainer;
                if (isCollaboration) {
                    backlogContainer = document.querySelector('[data-status="backlog"] .drop-zone') || 
                                      document.querySelector('[data-status="backlog"]') ||
                                      document.querySelector('.column[data-status="backlog"]') ||
                                      document.querySelector('.drop-zone');
                } else {
                    backlogContainer = document.querySelector('#task-card') || 
                                      document.querySelector('.not-yet-started') ||
                                      document.querySelector('.drop-zone') ||
                                      document.querySelector('.task-container');
                }
                
                if (!backlogContainer) {
                    console.error('Could not find container for new task');
                    document.body.appendChild(taskElement);
                } else {
                    const emptyState = backlogContainer.querySelector('.empty-state');
                    if (emptyState) {
                        emptyState.remove();
                    }
                    
                    backlogContainer.appendChild(taskElement);
                
                    taskElement.classList.add('new-task');
                }
                
                taskInput.value = '';
                timeInput.value = '';
                
                setTimeout(() => {
                    addTaskBtn.classList.remove('loading');
                    addTaskBtn.innerHTML = '<i class="fa-solid fa-plus"></i> Add Task';
                    addTaskBtn.style.background = '';
                }, 2000);

                // if (!isCollaboration) {
                //     sortTasks();
                // }
            })
            .catch(error => {
                console.error('Error:', error);
                addTaskBtn.innerHTML = '<i class="fa-solid fa-exclamation-triangle"></i> Error';
                addTaskBtn.style.background = 'linear-gradient(135deg, #ef4444, #dc2626)';
                
                setTimeout(() => {
                    addTaskBtn.classList.remove('loading');
                    addTaskBtn.innerHTML = '<i class="fa-solid fa-plus"></i> Add Task';
                    addTaskBtn.style.background = '';
                }, 2000);
            });
        } else {
            // shake animation for empty input
            taskInput.style.animation = 'shake 0.5s ease-in-out';
            taskInput.focus();
            setTimeout(() => {
                taskInput.style.animation = '';
            }, 500);
        }
    }
}