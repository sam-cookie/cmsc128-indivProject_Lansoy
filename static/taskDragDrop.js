export function initializeDragDrop() {
    // Module is initialized through setupDropZones
}

export function sortTasks(container = null) {
    // if container not passed, sort all drop-zones
    const containers = container ? [container] : document.querySelectorAll('.drop-zone');

    containers.forEach(zone => {
        const tasks = Array.from(zone.querySelectorAll('.task-card'));

        tasks.sort((a, b) => {
            const priorityOrder = { high: 1, mid: 2, low: 3 };
            const aPriority = Object.keys(priorityOrder).find(p => a.classList.contains(p));
            const bPriority = Object.keys(priorityOrder).find(p => b.classList.contains(p));

            // compare priority
            if (priorityOrder[aPriority] !== priorityOrder[bPriority]) {
                return priorityOrder[aPriority] - priorityOrder[bPriority];
            }

            // compare date + time
            const aDate = new Date(`${a.querySelector('.task-date')?.textContent} ${a.querySelector('.task-time')?.textContent}`);
            const bDate = new Date(`${b.querySelector('.task-date')?.textContent} ${b.querySelector('.task-time')?.textContent}`);
            return aDate - bDate;
        });

        tasks.forEach(task => zone.appendChild(task));
    });
}

export function setupDragAndDrop(taskElement) {
    if (!taskElement.draggable) {
        taskElement.draggable = true;
    }

    taskElement.addEventListener('dragstart', function(e) {
        e.dataTransfer.setData('text/plain', taskElement.dataset.id);
        e.dataTransfer.effectAllowed = 'move';
        taskElement.classList.add('dragging');
        
        setTimeout(() => {
            taskElement.style.display = 'none';
        }, 0);
    });

    taskElement.addEventListener('dragend', function(e) {
        taskElement.classList.remove('dragging');
        taskElement.style.display = '';
        document.querySelectorAll('.drop-zone').forEach(zone => {
            zone.classList.remove('drag-over');
        });
    });
}

export function setupDropZones() {
    const dropZones = document.querySelectorAll('.drop-zone');
    
    dropZones.forEach(zone => {
        zone.addEventListener('dragover', function(e) {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
            zone.classList.add('drag-over');
        });

        zone.addEventListener('dragleave', function(e) {
            if (!zone.contains(e.relatedTarget)) {
                zone.classList.remove('drag-over');
            }
        });

        zone.addEventListener('drop', function(e) {
            e.preventDefault();
            zone.classList.remove('drag-over');
            
            const taskId = e.dataTransfer.getData('text/plain');
            const draggedTask = document.querySelector(`[data-id="${taskId}"]`);
            const newStatus = zone.closest('.column').dataset.status;
            
            if (draggedTask && newStatus) {
                const isCollabTask = draggedTask.hasAttribute('data-collab');
                if (isCollabTask) {
                    moveCollabTaskToStatus(taskId, newStatus, draggedTask, zone);
                } else {
                    moveTaskToStatus(taskId, newStatus, draggedTask, zone);
                }
            }
        });
    });
}

function moveTaskToStatus(taskId, newStatus, taskElement, targetZone) {
    fetch(`/update_task_status/${taskId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            taskElement.remove();

            if (targetZone.dataset.empty === 'true') {
                targetZone.innerHTML = '';
                targetZone.removeAttribute('data-empty');
            }

            targetZone.appendChild(taskElement);

            // sort tasks after appending
            sortTasks(targetZone);

            showTaskMovedFeedback(taskElement, newStatus);
        } else {
            console.error('Failed to update task status');
            window.location.reload();
        }
    })
    .catch(error => {
        console.error('Error updating task status:', error);
        window.location.reload();
    });
}

function moveCollabTaskToStatus(taskId, newStatus, taskElement, targetZone) {
    fetch(`/update_collab_task_status/${taskId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            taskElement.remove();

            if (targetZone.querySelector('.empty-state')) {
                targetZone.innerHTML = '';
            }

            targetZone.appendChild(taskElement);

            // sort tasks after appending
            sortTasks(targetZone);

            showTaskMovedFeedback(taskElement, newStatus);
        } else {
            console.error('Failed to update task status');
            window.location.reload();
        }
    })
    .catch(error => {
        console.error('Error updating task status:', error);
        window.location.reload();
    });
}

function showTaskMovedFeedback(taskElement, status) {
    taskElement.style.transform = 'scale(1.05)';
    taskElement.style.boxShadow = '0 8px 25px #043915';
    
    setTimeout(() => {
        taskElement.style.transform = '';
        taskElement.style.boxShadow = '';
    }, 500);

    const toast = document.createElement('div');
    toast.className = 'status-toast';
    
    const statusText = {
        'backlog': 'moved to Backlog',
        'in-progress': 'moved to In Progress',
        'completed': 'moved to Completed'
    };
    
    toast.textContent = `Task ${statusText[status]}!`;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('slide-out');
        setTimeout(() => toast.remove(), 300);
    }, 2000);
}
