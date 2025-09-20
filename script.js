function addDescription() {
    const descriptionInput = document.getElementById('description-input');
    const taskInput = document.getElementById('task-input');
    const taskList = document.getElementById('task-list');

    taskInput.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' && descriptionInput.value.trim() !== '') {
            const description = document.createElement('p');
            description.textContent = descriptionInput.value.trim();
            taskList.appendChild(description);
            descriptionInput.value = '';
        }
    });
}


function addTitle() {
    const titleInput = document.getElementById('title-input');
    const sidebarTitle = document.getElementById('sidebar-title');

    titleInput.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' && titleInput.value.trim() !== '') {
            sidebarTitle.textContent = titleInput.value.trim();
            titleInput.value = '';
        }
    });
}

function addTask() {
    const taskInput = document.getElementById('task-input');
    const taskList = document.getElementById('task-list');
    const dateInput = document.getElementById('date-input-input');
    const sidebarTitle = document.getElementById('sidebar-title');

    taskInput.addEventListener('keydown', function(event) {
        if (
            event.key === 'Enter' &&
            taskInput.value.trim() !== '' &&
            dateInput.value.trim() !== ''
        ) {
            const li = document.createElement('li');
            li.textContent = `${taskInput.value.trim()} (DUE: ${dateInput.value.trim()})`;
                if (taskList.children.length === 0) {
                    sidebarTitle.style.display = "none";
                }
            });

            li.appendChild(delBtn);
            taskList.appendChild(li);

    
            sidebarTitle.style.display = "block";

            taskInput.value = '';
            dateInput.value = '';
        }
    });
}


document.addEventListener('DOMContentLoaded', function() {
    addTask();
    addTitle();
    addDescription();
});
