import { initializeTaskCreation } from './taskCreation.js';
import { initializeTaskDeletion } from './taskDeletion.js';
import { initializeTaskEdit } from './taskEdit.js';
import { initializeTaskEvents, attachTaskEvents, addSecondsDisplay } from './taskEvents.js';
import { initializeDragDrop, setupDropZones } from './taskDragDrop.js';
import { sortTasks } from './taskSort.js';
// import { initializeSidebar } from './sidebar.js';

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all modules
    initializeTaskCreation();
    initializeTaskDeletion();
    initializeTaskEdit();
    initializeTaskEvents();
    initializeDragDrop();
    // initializeSidebar();
    
    // Set up drop zones
    setupDropZones();
    
    // Set today's date as default
    const dateInput = document.getElementById('date-input');
    const today = new Date().toISOString().split('T')[0];
    if (dateInput) dateInput.value = today;

    // Attach events to existing tasks
    document.querySelectorAll('.task-card').forEach(taskDiv => {
        attachTaskEvents(taskDiv);
        addSecondsDisplay(taskDiv);
    });
});