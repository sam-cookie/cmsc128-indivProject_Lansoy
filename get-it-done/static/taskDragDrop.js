export function initializeDragDrop() {
    // Module is initialized through setupDropZones
}

export function setupDragAndDrop(taskElement) {
    // to make sure task card is able to drag
    if (!taskElement.draggable) {
        taskElement.draggable = true;
    }

    //  start drag
    taskElement.addEventListener('dragstart', function(e) {
        e.dataTransfer.setData('text/plain', taskElement.dataset.id);
        e.dataTransfer.effectAllowed = 'move';
        taskElement.classList.add('dragging');
        
        // hide the original element
        setTimeout(() => {
            taskElement.style.display = 'none';
        }, 0);
    });

    // end of drag
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
            // Only remove drag-over if we're actually leaving the zone
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
    // Update task status in database
    fetch(`/update_task_status/${taskId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            // remove task from current 
            taskElement.remove();
            
            // update target zone
            if (targetZone.dataset.empty === 'true') {
                // Remove empty state
                targetZone.innerHTML = '';
                targetZone.removeAttribute('data-empty');
            }
            
            // add task to new location
            targetZone.appendChild(taskElement);
            
            // show toasty!
            showTaskMovedFeedback(taskElement, newStatus);
        } else {
            console.error('Failed to update task status');
            // if update failed, reload back to location
            window.location.reload();
        }
    })
    .catch(error => {
        console.error('Error updating task status:', error);
        // Restore original position if error occurred
        window.location.reload();
    });
}

function moveCollabTaskToStatus(taskId, newStatus, taskElement, targetZone) {
    // Update task status in database
    fetch(`/update_collab_task_status/${taskId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            // remove task from current 
            taskElement.remove();
            
            // update target zone
            if (targetZone.querySelector('.empty-state')) {
                targetZone.innerHTML = '';
            }
            
            // add task to new location
            targetZone.appendChild(taskElement);
            
            // show toasty!
            showTaskMovedFeedback(taskElement, newStatus);
        } else {
            console.error('Failed to update task status');
            // if update failed, reload back to location
            window.location.reload();
        }
    })
    .catch(error => {
        console.error('Error updating task status:', error);
        // Restore original position if error occurred
        window.location.reload();
    });
}

function showTaskMovedFeedback(taskElement, status) {
    // animation to show the task was moved
    taskElement.style.transform = 'scale(1.05)';
    taskElement.style.boxShadow = '0 8px 25px #043915';
    
    setTimeout(() => {
        taskElement.style.transform = '';
        taskElement.style.boxShadow = '';
    }, 500);

    // toast
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