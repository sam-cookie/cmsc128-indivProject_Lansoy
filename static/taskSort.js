export function sortTasks() {
    const container = document.querySelector('.not-yet-started'); 
    if (!container) return;
    
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
        const aDate = new Date(`${a.querySelector('.date-time')?.textContent}`);
        const bDate = new Date(`${b.querySelector('.date-time')?.textContent}`);
        return aDate - bDate;
    });

    tasks.forEach(task => container.appendChild(task)); 
}