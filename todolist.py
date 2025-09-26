from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

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
            time TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        priority = request.form['priority']
        date = request.form['date']
        time = request.form['time']
        conn = sqlite3.connect('tododatabase.db')
        c = conn.cursor()
        c.execute('INSERT INTO tasks (name, priority, date, time) VALUES (?, ?, ?, ?)',
                  (name, priority, date, time))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    conn = sqlite3.connect('tododatabase.db')
    c = conn.cursor()
    c.execute('SELECT * FROM tasks')
    tasks = c.fetchall()
    conn.close()
    return render_template('index.html', tasks=tasks)

if __name__ == '__main__':
    app.run(debug=True)