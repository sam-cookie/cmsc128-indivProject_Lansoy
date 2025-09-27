document.addEventListener('DOMContentLoaded', function() {
    const addTaskBtn = document.getElementById('add-task-button');
    const taskInput = document.getElementById('task-input');
    const prioritySelect = document.getElementById('priority-select');
    const dateInput = document.getElementById('date-input-input');
    const timeInput = document.getElementById('time-input');
    const taskCardContainer = document.getElementById('task-card');

    document.querySelectorAll('.task-card').forEach(taskDiv => {
        attachTaskEvents(taskDiv);
    });

    // add new task
    addTaskBtn.addEventListener('click', function() {
        const taskText = taskInput.value.trim();
        const priority = prioritySelect.value;
        const date = dateInput.value;
        const time = timeInput.value;

        if (taskText !== '') {
            fetch('/add_task', {
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
                window.location.reload(); 
            });
        }
    });

    function sortTasks() {
        const container = document.querySelector('.not-yet-started'); // or whichever column
        const tasks = Array.from(container.querySelectorAll('.task-card'));

        tasks.sort((a, b) => {
            const priorityOrder = { high: 1, mid: 2, low: 3 };
            const aPriority = Object.keys(priorityOrder).find(p => a.classList.contains(p));
            const bPriority = Object.keys(priorityOrder).find(p => b.classList.contains(p));

            // compare priority
            if (priorityOrder[aPriority] !== priorityOrder[bPriority]) {
                return priorityOrder[aPriority] - priorityOrder[bPriority];
            }

            // compare date + time
            const aDate = new Date(`${a.querySelector('.date-time').textContent}`);
            const bDate = new Date(`${b.querySelector('.date-time').textContent}`);
            return aDate - bDate;
        });

        tasks.forEach(task => container.appendChild(task)); // re-append in order
    }   



    function attachTaskEvents(taskDiv) {
        const deleteIcon = taskDiv.querySelector('.fa-trash');
        const editIcon = taskDiv.querySelector('.fa-pen');
        const taskId = taskDiv.dataset.id;

        // delete
        deleteIcon.addEventListener('click', () => {
            if (confirm('Are you sure you want to delete this task?')) {
                fetch(`/delete_task/${taskId}`, { method: 'DELETE' })
                    .then(res => res.json())
                    .then(data => {
                        if (data.success) taskDiv.remove();
                    });
            }
        });

        // edit
        editIcon.addEventListener('click', () => {
            const taskNameDiv = taskDiv.querySelector('div:first-child');
            const dateTimeDiv = taskDiv.querySelector('.date-time');
            const [oldDate, oldTime] = dateTimeDiv.textContent.split(' ');

            const editForm = document.createElement('form');
            editForm.className = 'edit-overlay';

            const editTaskInput = document.createElement('input');
            editTaskInput.type = 'text';
            editTaskInput.value = taskNameDiv.textContent;

            const editPrioritySelect = document.createElement('select');
            ['high', 'mid', 'low'].forEach(optionVal => {
                const opt = document.createElement('option');
                opt.value = optionVal;
                opt.textContent = optionVal.charAt(0).toUpperCase() + optionVal.slice(1);
                if (taskDiv.classList.contains(optionVal)) {
                    opt.selected = true;
                }
                editPrioritySelect.appendChild(opt);
            });


            const editDateInput = document.createElement('input');
            editDateInput.type = 'date';
            editDateInput.value = oldDate;

            const editTimeInput = document.createElement('input');
            editTimeInput.type = 'time';
            editTimeInput.value = oldTime;

            const saveBtn = document.createElement('button');
            saveBtn.type = 'submit';
            saveBtn.textContent = 'Save';

            const cancelBtn = document.createElement('button');
            cancelBtn.type = 'button';
            cancelBtn.textContent = 'Cancel';

            editForm.appendChild(editTaskInput);
            editForm.appendChild(editPrioritySelect);
            editForm.appendChild(editDateInput);
            editForm.appendChild(editTimeInput);
            editForm.appendChild(saveBtn);
            editForm.appendChild(cancelBtn);

            document.body.appendChild(editForm);
            editForm.style.display = "flex"; 

            cancelBtn.addEventListener('click', function(e) {
                e.preventDefault();
                editForm.remove();
            });

            editForm.addEventListener('submit', function(e) {
                e.preventDefault();
                fetch(`/edit_task/${taskId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        name: editTaskInput.value,
                        date: editDateInput.value,
                        time: editTimeInput.value,
                        priority: editPrioritySelect.value
                    })
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        taskNameDiv.textContent = editTaskInput.value;
                        dateTimeDiv.textContent = `${editDateInput.value} ${editTimeInput.value}`;
                        taskDiv.classList.remove('high', 'mid', 'low');
                        taskDiv.classList.add(editPrioritySelect.value);
                        editForm.remove();
                        sortTasks(); 
                    }
                });
            });
        });
    }
});
