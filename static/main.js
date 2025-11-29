import { initializeTaskCreation } from './taskCreation.js';
import { initializeTaskDeletion } from './taskDeletion.js';
import { initializeTaskEdit } from './taskEdit.js';
import { initializeTaskEvents, attachTaskEvents, addSecondsDisplay } from './taskEvents.js';
import { initializeDragDrop, setupDropZones } from './taskDragDrop.js';
import { sortTasks } from './taskSort.js';

document.addEventListener('DOMContentLoaded', function() {

    console.log("DOM loaded, initializing modules...");

    // initialize modules
    initializeTaskCreation();
    initializeTaskDeletion();
    initializeTaskEdit();
    initializeTaskEvents();
    initializeDragDrop();
    setupDropZones();

    const dateInput = document.getElementById('date-input');
    const today = new Date().toISOString().split('T')[0];
    if (dateInput) {
        dateInput.value = today;
        console.log("Date input found, set to today:", today);
    } else {
        console.warn("Date input NOT found!");
    }

    document.querySelectorAll('.task-card').forEach(taskDiv => {
        attachTaskEvents(taskDiv);
        addSecondsDisplay(taskDiv);
    });

    // sidebar toggle
    const sidebar = document.getElementById("sidebar");
    const toggleBtn = document.getElementById("sidebarToggle");
    const mainContent = document.getElementById("mainContent");

    console.log("Sidebar:", sidebar);
    console.log("Toggle button:", toggleBtn);
    console.log("Main content:", mainContent);

    if (sidebar && toggleBtn && mainContent) {
        toggleBtn.addEventListener("click", () => {
            console.log("Sidebar toggle clicked!");
            sidebar.classList.toggle("collapsed");
            document.body.classList.toggle("sidebar-collapsed");

            const icon = toggleBtn.querySelector("i");
            if (sidebar.classList.contains("collapsed")) {
                icon.style.transform = "rotate(180deg)";
                console.log("Sidebar collapsed");
            } else {
                icon.style.transform = "rotate(0deg)";
                console.log("Sidebar expanded");
            }
        });
    } else {
        console.error("Sidebar toggle setup failed: some elements are missing!");
    }
});
