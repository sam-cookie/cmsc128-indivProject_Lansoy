import { attachTaskEvents, addSecondsDisplay } from './taskEvents.js';

const LIST_ID = document.querySelector('[data-collab="true"]') || document.getElementById('collab-list-id') ? 
                document.getElementById('collab-list-id')?.value : null;

export function initializeTaskDeletion() {
    // Module is initialized through exported functions
}

export function deleteTaskWithUndo(taskElement, taskId) {
    // store task for undoing
    const taskData = {
        id: taskId,
        name: taskElement.querySelector('.task-name').textContent,
        priority: taskElement.classList.contains('high') ? 'high' : 
                 taskElement.classList.contains('mid') ? 'mid' : 'low',
        date: taskElement.querySelector('.task-date').textContent,
        time: taskElement.querySelector('.task-time').textContent.replace(/.*?(\d{1,2}:\d{2}).*/, '$1'),
        element: taskElement.cloneNode(true),
        parent: taskElement.parentElement
    };

    // delete animation
    taskElement.style.animation = 'fadeOut 0.3s ease-out';
    
    // Delete from database
    fetch(`/delete_task/${taskId}`, {
        method: 'DELETE'
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            // Remove from DOM after successful database deletion
            setTimeout(() => {
                taskElement.remove();
                showUndoNotification(taskData, false);
            }, 300);
        } else {
            console.error('Failed to delete task from database');
            // Restore animation if deletion failed
            taskElement.style.animation = '';
        }
    })
    .catch(error => {
        console.error('Error deleting task:', error);
        // Restore animation if deletion failed
        taskElement.style.animation = '';
    });
}

export function deleteCollabTaskWithUndo(taskElement, taskId) {
    // store task for undoing
    const taskData = {
        id: taskId,
        name: taskElement.querySelector('.task-name').textContent,
        priority: taskElement.classList.contains('high') ? 'high' : 
                 taskElement.classList.contains('mid') ? 'mid' : 'low',
        date: taskElement.querySelector('.task-date').textContent,
        time: taskElement.querySelector('.task-time').textContent.replace(/.*?(\d{1,2}:\d{2}).*/, '$1'),
        created_by: taskElement.querySelector('.task-meta small')?.textContent.replace('Created by: ', ''),
        element: taskElement.cloneNode(true),
        parent: taskElement.parentElement,
        isCollab: true
    };

    // delete animation
    taskElement.style.animation = 'fadeOut 0.3s ease-out';
    
    // Delete from database
    fetch(`/delete_collab_task/${taskId}`, {
        method: 'DELETE'
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            // Remove from DOM after successful database deletion
            setTimeout(() => {
                taskElement.remove();
                
                // Check if container is now empty and show empty state
                const container = taskData.parent;
                if (container.children.length === 0) {
                    const emptyState = document.createElement('div');
                    emptyState.className = 'empty-state';
                    emptyState.innerHTML = `
                        <i class="fa-solid fa-inbox"></i>
                        <p>No tasks in ${container.closest('.column').querySelector('h2').textContent.replace('↓', '').replace('→', '').replace('↑', '').trim()}</p>
                    `;
                    container.appendChild(emptyState);
                }
                
                showUndoNotification(taskData, true);
            }, 300);
        } else {
            console.error('Failed to delete task from database');
            // Restore animation if deletion failed
            taskElement.style.animation = '';
            alert(data.error || 'Failed to delete task');
        }
    })
    .catch(error => {
        console.error('Error deleting task:', error);
        // Restore animation if deletion failed
        taskElement.style.animation = '';
    });
}

function showUndoNotification(taskData, isCollab) {
    const undoNotification = document.createElement('div');
    undoNotification.className = 'undo-notification';

    const message = document.createElement('span');
    message.className = 'undo-message';
    message.textContent = 'Task deleted!';

    const countdown = document.createElement('span');
    countdown.className = 'undo-countdown';

    const undoButton = document.createElement('button');
    undoButton.className = 'undo-button';
    undoButton.textContent = 'Undo';

    undoNotification.appendChild(message);
    undoNotification.appendChild(countdown);
    undoNotification.appendChild(undoButton);
    document.body.appendChild(undoNotification);

    // countdown for undo
    let timeLeft = 5;
    countdown.textContent = timeLeft;

    const countdownInterval = setInterval(() => {
        timeLeft--;
        countdown.textContent = timeLeft;
        
        if (timeLeft <= 0) {
            clearInterval(countdownInterval);
            undoNotification.style.animation = 'slideOutToBottom 0.3s ease-in';
            setTimeout(() => undoNotification.remove(), 300);
        }
    }, 1000);

    // Undo functionality!!
    undoButton.addEventListener('click', () => {
        clearInterval(countdownInterval);
        if (isCollab) {
            undoCollabTask(taskData);
        } else {
            undoTask(taskData);
        }
        undoNotification.style.animation = 'slideOutToBottom 0.3s ease-in';
        setTimeout(() => undoNotification.remove(), 300);
    });
}

function undoTask(taskData) {
    // Restore task in database first
    fetch('/add_task', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            name: taskData.name,
            priority: taskData.priority,
            date: taskData.date,
            time: taskData.time
        })
    })
    .then(res => res.json())
    .then(newTask => {
        const restoredTask = taskData.element;
        restoredTask.setAttribute('data-id', newTask.id);
        taskData.parent.appendChild(restoredTask);
        
        // reattach event listeners when undo
        attachTaskEvents(restoredTask);
        addSecondsDisplay(restoredTask);

        // add redo animation
        restoredTask.style.animation = 'slideInFromTop 0.5s ease-out';
    })
    .catch(error => {
        console.error('Error restoring task:', error);
    });
    
    // show message for success undo
    const successToast = document.createElement('div');
    successToast.className = 'success-toast';
    
    successToast.textContent = 'Task restored!';
    document.body.appendChild(successToast);
    
    setTimeout(() => {
        successToast.style.animation = 'slideOutToRight 0.3s ease-in';
        setTimeout(() => successToast.remove(), 300);
    }, 2000);
}

function undoCollabTask(taskData) {
    // restore task in database first
    fetch(`/add_collab_task/${LIST_ID}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            name: taskData.name,
            priority: taskData.priority,
            date: taskData.date,
            time: taskData.time
        })
    })
    .then(res => res.json())
    .then(newTask => {
        const restoredTask = taskData.element;
        restoredTask.setAttribute('data-id', newTask.id);
        
    
        const metaElement = restoredTask.querySelector('.task-meta small');
        if (metaElement) {
            metaElement.textContent = `Created by: ${newTask.created_by}`;
        }
        
        taskData.parent.appendChild(restoredTask);
        
        const emptyState = taskData.parent.querySelector('.empty-state');
        if (emptyState) {
            emptyState.remove();
        }
        
        attachTaskEvents(restoredTask);

        restoredTask.style.animation = 'slideInFromTop 0.5s ease-out';
    })
    .catch(error => {
        console.error('Error restoring task:', error);
    });
    
    // show message for success undo
    const successToast = document.createElement('div');
    successToast.className = 'success-toast';
    
    successToast.textContent = 'Task restored!';
    document.body.appendChild(successToast);
    
    setTimeout(() => {
        successToast.style.animation = 'slideOutToRight 0.3s ease-in';
        setTimeout(() => successToast.remove(), 300);
    }, 2000);
}