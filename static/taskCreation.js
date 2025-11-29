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
            addTaskBtn.classList.add('loading');
            addTaskBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Adding...';
            
            // check if collab or not
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
                
                // SMARTER CONTAINER DETECTION
                let backlogContainer;
                if (isCollaboration) {
                    // For collaboration: use the same structure as collab_tasks.html
                    backlogContainer = document.querySelector('[data-status="backlog"] .drop-zone') || 
                                      document.querySelector('[data-status="backlog"]') ||
                                      document.querySelector('.column[data-status="backlog"] .drop-zone') ||
                                      document.querySelector('.drop-zone[data-status="backlog"]');
                } else {
                    // For personal tasks: handle both old and new structures
                    backlogContainer = document.querySelector('#task-card') || 
                                      document.querySelector('[data-status="backlog"] .drop-zone') ||
                                      document.querySelector('.column[data-status="backlog"] .drop-zone') ||
                                      document.querySelector('.drop-zone[data-status="backlog"]') ||
                                      document.querySelector('.drop-zone');
                }
                
                if (!backlogContainer) {
                    console.error('Could not find container for new task');
                    // Fallback: try to find any drop-zone in backlog column
                    const backlogColumn = document.querySelector('[data-status="backlog"]') || 
                                         document.querySelector('.column[data-status="backlog"]');
                    if (backlogColumn) {
                        backlogContainer = backlogColumn.querySelector('.drop-zone') || backlogColumn;
                    }
                }
                
                if (!backlogContainer) {
                    console.error('Still could not find container for new task');
                    document.body.appendChild(taskElement);
                } else {
                    // REMOVE EMPTY STATES FROM THE BACKLOG CONTAINER
                    removeAllEmptyStates(backlogContainer);
                    
                    backlogContainer.appendChild(taskElement);
                    taskElement.classList.add('new-task');
                    
                    // RE-INITIALIZE EMPTY STATES FOR ALL COLUMNS
                    initializeEmptyStates();
                }
                
                taskInput.value = '';
                timeInput.value = '';
                
                setTimeout(() => {
                    addTaskBtn.classList.remove('loading');
                    addTaskBtn.innerHTML = '<i class="fa-solid fa-plus"></i> Add Task';
                    addTaskBtn.style.background = '';
                }, 2000);
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

    // Initialize empty states on page load
    initializeEmptyStates();
}

// ADD THIS HELPER FUNCTION
function removeAllEmptyStates(container) {
    // Remove styled empty states
    const emptyStates = container.querySelectorAll('.empty-state');
    emptyStates.forEach(state => state.remove());
    
    // Remove any old text empty states
    const elements = container.querySelectorAll('p, i, div');
    elements.forEach(el => {
        if (el.textContent.includes('No tasks') || 
            el.textContent.includes('There are no tasks') ||
            el.classList.contains('fa-inbox') ||
            el.classList.contains('fa-hourglass-half') || 
            el.classList.contains('fa-trophy')) {
            el.remove();
        }
    });
}

function initializeEmptyStates() {
    // Find all drop zones and ensure they have proper empty states
    const dropZones = document.querySelectorAll('.drop-zone');
    
    dropZones.forEach(zone => {
        const hasTasks = zone.querySelector('.task-card');
        const hasEmptyState = zone.querySelector('.empty-state');
        
        // MORE AGGRESSIVE CLEANUP OF OLD EMPTY STATES
        // Remove any text nodes or elements that contain empty state messages
        const walker = document.createTreeWalker(
            zone,
            NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT,
            null,
            false
        );
        
        let node;
        const nodesToRemove = [];
        
        while (node = walker.nextNode()) {
            if (node.nodeType === Node.TEXT_NODE) {
                if (node.textContent.includes('There are no tasks') || 
                    node.textContent.includes('no tasks')) {
                    nodesToRemove.push(node);
                }
            } else if (node.nodeType === Node.ELEMENT_NODE) {
                if ((node.tagName === 'P' || node.tagName === 'I') && 
                    (node.textContent.includes('There are no tasks') || 
                     node.textContent.includes('no tasks')) &&
                    !node.closest('.empty-state')) {
                    nodesToRemove.push(node);
                }
            }
        }
        
        // Remove the identified nodes
        nodesToRemove.forEach(node => {
            if (node.parentNode) {
                node.parentNode.removeChild(node);
            }
        });

        // Now handle the proper empty state
        if (!hasTasks && !hasEmptyState) {
            // Create proper empty state
            const emptyState = document.createElement('div');
            emptyState.className = 'empty-state';
            
            const columnStatus = zone.closest('.column')?.dataset.status || 
                               zone.dataset.status || 
                               'backlog';
            
            let iconClass, message;
            
            switch(columnStatus) {
                case 'backlog':
                    iconClass = 'fa-inbox';
                    message = 'No tasks in backlog';
                    break;
                case 'in-progress':
                    iconClass = 'fa-hourglass-half';
                    message = 'No tasks in progress';
                    break;
                case 'completed':
                    iconClass = 'fa-trophy';
                    message = 'No completed tasks';
                    break;
                default:
                    iconClass = 'fa-inbox';
                    message = 'No tasks';
            }
            
            emptyState.innerHTML = `
                <i class="fa-solid ${iconClass}"></i>
                <p>${message}</p>
            `;
            
            zone.appendChild(emptyState);
        } else if (hasTasks && hasEmptyState) {
            // Remove empty state if there are tasks
            hasEmptyState.remove();
        }
    });
}