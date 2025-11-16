import { setupDragAndDrop } from './taskDragDrop.js';
import { deleteTaskWithUndo, deleteCollabTaskWithUndo } from './taskDeletion.js';
import { openEditModal } from './taskEdit.js';

export function initializeTaskEvents() {
    // Module is initialized through exported functions
}

export function attachTaskEvents(taskDiv) {
    const deleteIcon = taskDiv.querySelector('.fa-trash');
    const editIcon = taskDiv.querySelector('.fa-pen');
    const taskId = taskDiv.dataset.id;
    const isCollabTask = taskDiv.hasAttribute('data-collab');

    // drag and drop functionality
    setupDragAndDrop(taskDiv);

    // delete
    deleteIcon.addEventListener('click', (e) => {
        e.stopPropagation();
        
        // confirmation before deleting task
        const confirmed = confirm('Are you sure you want to delete this task?');
        if (confirmed) {
            if (isCollabTask) {
                deleteCollabTaskWithUndo(taskDiv, taskId);
            } else {
                deleteTaskWithUndo(taskDiv, taskId);
            }
        }
    });

    // edit
    editIcon.addEventListener('click', (e) => {
        e.stopPropagation();
        openEditModal(taskDiv, taskId, isCollabTask);
    });
}

export function addSecondsDisplay(taskDiv) {
    const dateTimeDiv = taskDiv.querySelector('.date-time');
    if (!dateTimeDiv) return;

    // Create seconds display element
    const secondsDisplay = document.createElement('div');
    secondsDisplay.className = 'seconds-display';
    dateTimeDiv.appendChild(secondsDisplay);

    // Add hover event listeners
    dateTimeDiv.addEventListener('mouseenter', function() {
        const timeText = dateTimeDiv.textContent.trim();
        const timeMatch = timeText.match(/(\d{1,2}):(\d{2})/);
        
        if (timeMatch) {
            const hours = parseInt(timeMatch[1]);
            const minutes = parseInt(timeMatch[2]);
            const seconds = Math.floor(Math.random() * 60); // Random seconds for demo
            const formattedTime = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            secondsDisplay.textContent = formattedTime;
        }
    });

    dateTimeDiv.addEventListener('mouseleave', function() {
        secondsDisplay.textContent = '';
    });
}

export function createTaskElement(task) {
    const isCollaboration = document.querySelector('[data-collab="true"]') || 
                           document.getElementById('collab-list-id');
    
    const taskDiv = document.createElement('div');
    taskDiv.className = `task-card ${task.priority}`;
    taskDiv.setAttribute('data-id', task.id);
    taskDiv.setAttribute('draggable', 'true');
    if (isCollaboration) {
        taskDiv.setAttribute('data-collab', 'true');
    }
    
    // Collaborative tasks include created_by, personal ones don't
    const taskMeta = isCollaboration ? 
        `<div class="task-meta">
            <small>Created by: ${task.created_by}</small>
        </div>` : '';
    
    taskDiv.innerHTML = `
        <div class="task-header">
            <div class="task-name">${task.name}</div>
            <div class="task-priority-badge ${task.priority}">${task.priority.charAt(0).toUpperCase() + task.priority.slice(1)}</div>
        </div>
        <div class="task-content">
            <div class="task-date">${task.date}</div>
            <div class="task-time">
                <i class="fa-solid fa-clock"></i>
                ${task.time}
            </div>
        </div>
        ${taskMeta}
        <div class="task-actions">
            <i class="fa-solid fa-pen" title="Edit task"></i>
            <i class="fa-solid fa-trash" title="Delete task"></i>
        </div>
    `;
    
    // Attach event listeners
    attachTaskEvents(taskDiv);
    addSecondsDisplay(taskDiv);
    
    return taskDiv;
}