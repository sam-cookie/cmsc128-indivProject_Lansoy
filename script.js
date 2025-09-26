document.addEventListener('DOMContentLoaded', function() {
    const addTaskBtn = document.getElementById('add-task-button');
    const taskInput = document.getElementById('task-input');
    const prioritySelect = document.getElementById('priority-select');
    const dateInput = document.getElementById('date-input-input');
    const timeInput = document.getElementById('time-input');
    const notYetStartedDiv = document.querySelector('.not-yet-started');

    addTaskBtn.addEventListener('click', function() {
        const taskText = taskInput.value.trim();
        const priority = prioritySelect.value;
        const date = dateInput.value;
        const time = timeInput.value;

        if (taskText !== '') {
            const taskDiv = document.createElement('div');
            taskDiv.className = 'task-card';

            const taskNameDiv = document.createElement('div');
            taskNameDiv.textContent = taskText;

            const dateTimeDiv = document.createElement('div');
            dateTimeDiv.className = 'date-time';
            dateTimeDiv.textContent = `${date} ${time}`;

            if (priority === 'high') {
                taskDiv.style.backgroundColor = '#662019ff';
                taskDiv.style.color = '#fff';
            } else if (priority === 'mid') {
                taskDiv.style.backgroundColor = '#bc7474';
                taskDiv.style.color = '#fff';
            } else if (priority === 'low') {
                taskDiv.style.backgroundColor = '#d0baba';
                taskDiv.style.color = '#333';
            }

            const deleteIcon = document.createElement('i');
            deleteIcon.className = 'fa-solid fa-trash';
            deleteIcon.style.cursor = 'pointer';

            const editIcon = document.createElement('i');
            editIcon.className = 'fa-solid fa-pen';
            editIcon.style.cursor = 'pointer';

            const iconContainer = document.createElement('div');
            iconContainer.style.display = 'flex';
            iconContainer.style.gap = '10px';
            iconContainer.appendChild(editIcon);
            iconContainer.appendChild(deleteIcon);

            deleteIcon.addEventListener('click', function() {
                if (confirm('Are you sure you want to delete this task?')) {
                    taskDiv.remove();
                }
            });


            editIcon.addEventListener('click', function() {
                const editForm = document.createElement('form');
                editForm.style.display = 'flex';
                editForm.style.gap = '8px';

                const editTaskInput = document.createElement('input');
                editTaskInput.type = 'text';
                editTaskInput.value = taskNameDiv.textContent;
                editTaskInput.style.flex = '1';

                const editDateInput = document.createElement('input');
                editDateInput.type = 'date';
                editDateInput.value = date;

                const editTimeInput = document.createElement('input');
                editTimeInput.type = 'time';
                editTimeInput.value = time;

                const saveBtn = document.createElement('button');
                saveBtn.type = 'submit';
                saveBtn.textContent = 'Save';

                const cancelBtn = document.createElement('button');
                cancelBtn.type = 'button';
                cancelBtn.textContent = 'Cancel';

                editForm.appendChild(editTaskInput);
                editForm.appendChild(editDateInput);
                editForm.appendChild(editTimeInput);
                editForm.appendChild(saveBtn);
                editForm.appendChild(cancelBtn);

                taskDiv.innerHTML = '';
                taskDiv.appendChild(editForm);

                cancelBtn.addEventListener('click', function() {

                    taskDiv.innerHTML = '';
                    taskDiv.appendChild(taskNameDiv);
                    taskDiv.appendChild(dateTimeDiv);
                    taskDiv.appendChild(iconContainer);
                });

                editForm.addEventListener('submit', function(e) {
                    e.preventDefault();
                    taskNameDiv.textContent = editTaskInput.value;
                    dateTimeDiv.textContent = `${editDateInput.value} ${editTimeInput.value}`;
                    taskDiv.innerHTML = '';
                    taskDiv.appendChild(taskNameDiv);
                    taskDiv.appendChild(dateTimeDiv);
                    taskDiv.appendChild(iconContainer);
                });
            });

            taskDiv.appendChild(taskNameDiv);
            taskDiv.appendChild(dateTimeDiv);
            taskDiv.appendChild(iconContainer);

            const taskCardContainer = document.getElementById('task-card');
            taskCardContainer.appendChild(taskDiv);

            taskInput.value = '';
            dateInput.value = '';
            timeInput.value = '';
            prioritySelect.value = 'high';
        }
    });
});