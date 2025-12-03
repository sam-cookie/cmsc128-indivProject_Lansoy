from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
import sqlite3

personal_bp = Blueprint('personal', __name__)

# DB files
DB_NAME = "accounts.db"
TASK_DB = "todo.db"

@personal_bp.route("/profile")
def profile():
    username = session.get("username") 

    user_data = None
    if username:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT full_name, email, username FROM accounts WHERE username=?", (username,))
            user = cursor.fetchone()
            if user:
                user_data = {"full_name": user[0], "email": user[1], "username": user[2]}

    with sqlite3.connect(TASK_DB) as conn:
        cursor = conn.cursor()
        if username:
            cursor.execute("SELECT * FROM tasks WHERE username=? AND status='backlog'", (username,))
            backlog_tasks = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

            cursor.execute("SELECT * FROM tasks WHERE username=? AND status='in-progress'", (username,))
            in_progress_tasks = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

            cursor.execute("SELECT * FROM tasks WHERE username=? AND status='completed'", (username,))
            completed_tasks = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
        else:
            cursor.execute("SELECT * FROM tasks WHERE status='backlog'")
            backlog_tasks = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

            cursor.execute("SELECT * FROM tasks WHERE status='in-progress'")
            in_progress_tasks = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

            cursor.execute("SELECT * FROM tasks WHERE status='completed'")
            completed_tasks = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

    return render_template(
        "profile.html",
        user=user_data,
        username=username,
        tasks=backlog_tasks,
        in_progress_tasks=in_progress_tasks,
        completed_tasks=completed_tasks
    )


@personal_bp.route("/add_task", methods=["POST"])
def add_task():
    if "username" not in session:
        return jsonify({"error": "Not logged in"}), 401
    data = request.get_json()
    name = data.get("name")
    priority = data.get("priority")
    date = data.get("date")
    time = data.get("time")
    username = session["username"]

    if not name:
        return jsonify({"error": "Task name required"}), 400

    with sqlite3.connect(TASK_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (username, name, priority, date, time) VALUES (?, ?, ?, ?, ?)",
                       (username, name, priority, date, time))
        task_id = cursor.lastrowid
        conn.commit()

    return jsonify({"id": task_id, "name": name, "priority": priority, "date": date, "time": time})

@personal_bp.route("/edit_task/<int:task_id>", methods=["PUT"])
def edit_task(task_id):
    data = request.get_json()
    name = data.get("name")
    priority = data.get("priority")
    date = data.get("date")
    time = data.get("time")

    with sqlite3.connect(TASK_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET name=?, priority=?, date=?, time=? WHERE id=?", (name, priority, date, time, task_id))
        conn.commit()
    return jsonify({"success": True})

@personal_bp.route("/delete_task/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    with sqlite3.connect(TASK_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        conn.commit()
    return jsonify({"success": True})

@personal_bp.route("/update_task_status/<int:task_id>", methods=["PUT"])
def update_task_status(task_id):
    data = request.get_json()
    status = data.get("status")
    if status not in ["backlog", "in-progress", "completed"]:
        return jsonify({"success": False, "error": "Invalid status"})
    with sqlite3.connect(TASK_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET status=? WHERE id=?", (status, task_id))
        conn.commit()
    return jsonify({"success": True})