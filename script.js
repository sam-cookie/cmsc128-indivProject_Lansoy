function addDescription(element){
    const descriptionInput = document.getElementById('description-input');

    taskInput.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' && descriptionInput.value.trim() !== '') {
            const description = document.createElement('p');
            description.textContent = descriptionInput.value.trim();
            taskList.appendChild(description);
            descriptionInput.value = '';
        }
    }
    );
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

function addTask(element) {
    const taskInput = document.getElementById('task-input');
    const taskList = document.getElementById('task-list'); 


    taskInput.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' && taskInput.value.trim() !== '') {
            const li = document.createElement('li');
            li.textContent = taskInput.value.trim();
            taskList.appendChild(li);
            taskInput.value = '';
        }
    });
}


document.addEventListener('DOMContentLoaded', function() {
    addTask();
    addTitle();
    addDescription();
});
