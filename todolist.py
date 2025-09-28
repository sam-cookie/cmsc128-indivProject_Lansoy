from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('tododatabase.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            priority TEXT,
            date TEXT,
            time TEXT,
            status TEXT DEFAULT 'backlog'
        )
    ''')
    
    try:
        c.execute('ALTER TABLE tasks ADD COLUMN status TEXT DEFAULT "backlog"')
        conn.commit()
    except sqlite3.OperationalError:
        pass
    
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    conn = sqlite3.connect('tododatabase.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''
        SELECT * FROM tasks
        WHERE status = 'backlog' OR status IS NULL
        ORDER BY 
            CASE priority
                WHEN 'high' THEN 1
                WHEN 'mid'  THEN 2
                WHEN 'low'  THEN 3
            END,
            date ASC,
            time ASC
    ''')
    backlog_tasks = c.fetchall()
    
    c.execute('''
        SELECT * FROM tasks
        WHERE status = 'in-progress'
        ORDER BY 
            CASE priority
                WHEN 'high' THEN 1
                WHEN 'mid'  THEN 2
                WHEN 'low'  THEN 3
            END,
            date ASC,
            time ASC
    ''')
    in_progress_tasks = c.fetchall()
    
    c.execute('''
        SELECT * FROM tasks
        WHERE status = 'completed'
        ORDER BY 
            CASE priority
                WHEN 'high' THEN 1
                WHEN 'mid'  THEN 2
                WHEN 'low'  THEN 3
            END,
            date ASC,
            time ASC
    ''')
    completed_tasks = c.fetchall()
    
    conn.close()
    return render_template('index.html', 
                         tasks=backlog_tasks, 
                         in_progress_tasks=in_progress_tasks,
                         completed_tasks=completed_tasks)

@app.route('/add_task', methods=['POST'])
def add_task():
    data = request.get_json()
    name = data['name']
    priority = data['priority']
    date = data['date']
    time = data['time']
    conn = sqlite3.connect('tododatabase.db')
    c = conn.cursor()
    c.execute('INSERT INTO tasks (name, priority, date, time) VALUES (?, ?, ?, ?)',
              (name, priority, date, time))
    conn.commit()
    task_id = c.lastrowid
    conn.close()
    return jsonify({'id': task_id, 'name': name, 'priority': priority, 'date': date, 'time': time})

@app.route('/edit_task/<int:task_id>', methods=['PUT'])
def edit_task(task_id):
    data = request.get_json()
    name = data.get('name')
    date = data.get('date')
    time = data.get('time')
    priority = data.get('priority')

    conn = sqlite3.connect('tododatabase.db')
    c = conn.cursor()
    c.execute('''
        UPDATE tasks
        SET name = ?, date = ?, time = ?, priority = ?
        WHERE id = ?
    ''', (name, date, time, priority, task_id))
    conn.commit()
    conn.close()

    return jsonify({'success': True})

@app.route('/delete_task/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    conn = sqlite3.connect('tododatabase.db')
    c = conn.cursor()
    c.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/update_task_status/<int:task_id>', methods=['PUT'])
def update_task_status(task_id):
    data = request.get_json()
    status = data.get('status')
    
    if status not in ['backlog', 'in-progress', 'completed']:
        return jsonify({'success': False, 'error': 'Invalid status'})
    
    conn = sqlite3.connect('tododatabase.db')
    c = conn.cursor()
    c.execute('UPDATE tasks SET status = ? WHERE id = ?', (status, task_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})


if __name__ == '__main__':
    app.run(debug=True)