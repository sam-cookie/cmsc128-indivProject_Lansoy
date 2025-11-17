from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# DB files
DB_NAME = "accounts.db"
TASK_DB = "tododatabase.db"
COLLAB_DB = "collaborations.db"

def init_collaborations_db():
    if not os.path.exists(COLLAB_DB):
        with sqlite3.connect(COLLAB_DB) as conn:
            # Table for collaboration lists
            conn.execute("""
                CREATE TABLE collab_lists (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    list_name TEXT NOT NULL,
                    description TEXT,
                    owner_username TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table for collaboration members
            conn.execute("""
                CREATE TABLE collab_members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    list_id INTEGER NOT NULL,
                    member_username TEXT NOT NULL,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (list_id) REFERENCES collab_lists (id) ON DELETE CASCADE,
                    UNIQUE(list_id, member_username)
                )
            """)
            
            # Table for collaborative tasks
            conn.execute("""
                CREATE TABLE collab_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    list_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    priority TEXT,
                    date TEXT,
                    time TEXT,
                    status TEXT DEFAULT 'backlog',
                    created_by TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (list_id) REFERENCES collab_lists (id) ON DELETE CASCADE
                )
            """)
        print("Collaborations DB created.")
    else:
        print("Collaborations DB exists.")

def init_db():
    if not os.path.exists(DB_NAME):
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("""
                CREATE TABLE accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    security_question TEXT NOT NULL
                )
            """)
        print("Accounts DB created.")
    else:
        print("Accounts DB exists.")

def init_tasks_db():
    if not os.path.exists(TASK_DB):
        with sqlite3.connect(TASK_DB) as conn:
            conn.execute("""
                CREATE TABLE tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    name TEXT NOT NULL,
                    priority TEXT,
                    date TEXT,
                    time TEXT,
                    status TEXT DEFAULT 'backlog'
                )
            """)
        print("Tasks DB created.")
    else:
        print("Tasks DB exists.")

# --- ACCOUNT ROUTES ---
@app.route("/")
def home():
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    message = session.pop("message", None)
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM accounts WHERE username = ?", (username,))
            row = cursor.fetchone()

        if row and check_password_hash(row[0], password):
            session["username"] = username
            return redirect(url_for("profile"))
        else:
            error = "Invalid username or password."

    return render_template("accounts.html", error=error, message=message)

@app.route("/logout")
def logout():
    session.pop("username", None)
    session["message"] = "Logged out successfully."
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    message = None
    error = None

    if request.method == "POST":
        full_name = request.form["fullName"]
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]
        security_question = request.form["securityQuestion"]

        if len(password) < 8:
            error = "Password must be at least 8 characters long."
            return render_template("register.html", message=message, error=error)
        if "@" not in email:
            error = "Please enter a valid email address."
            return render_template("register.html", message=message, error=error)

        hashed_password = generate_password_hash(password)
        hashed_security_question = generate_password_hash(security_question)

        try:
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO accounts (full_name, email, username, password, security_question)
                    VALUES (?, ?, ?, ?, ?)
                """, (full_name, email, username, hashed_password, hashed_security_question))
                conn.commit()
            session["message"] = "Account created successfully! You can now log in."
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            error = "Username or email already exists."

    return render_template("register.html", message=message, error=error)

@app.route("/editpassword/<username>", methods=["GET", "POST"])
def edit_password(username):
    message = None
    error = None

    if request.method == "POST":
        new_password = request.form["password"]
        if len(new_password) < 8:
            error = "Password must be at least 8 characters long."
            return render_template("editpassword.html", message=message, error=error)

        hashed_password = generate_password_hash(new_password)
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE accounts SET password = ? WHERE username = ?", (hashed_password, username))
            conn.commit()

        session["message"] = "Password updated successfully! You may login now."
        return redirect(url_for("login"))

    return render_template("editpassword.html", username=username, message=message)

@app.route("/forgotpassword", methods=["GET", "POST"])
def forgot_password():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        answer = request.form["securityQuestion"]

        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT security_question FROM accounts WHERE username = ?", (username,))
            row = cursor.fetchone()

        if not row:
            error = "User not found."
            return render_template("forgotpassword.html", error=error)

        if check_password_hash(row[0], answer):
            session["message"] = "Security answer correct. Please set your new password."
            return redirect(url_for("edit_password", username=username))
        else:
            error = "Wrong answer. Please try again."

    return render_template("forgotpassword.html", error=error)

@app.route("/editprofile/<username>", methods=["GET", "POST"])
def edit_profile(username):
    message = None
    error = None
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT full_name, email, username FROM accounts WHERE username = ?", (username,))
        user = cursor.fetchone()
    if not user:
        session["message"] = "User not found."
        return redirect(url_for("login"))

    if request.method == "POST":
        new_name = request.form["fullName"]
        new_username = request.form["username"]
        new_email = request.form["email"]
        new_password = request.form["password"]

        try:
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                if new_password.strip() == "":
                    cursor.execute("""
                        UPDATE accounts SET full_name=?, username=?, email=? WHERE username=?
                    """, (new_name, new_username, new_email, username))
                else:
                    if len(new_password) < 8:
                        error = "Password must be at least 8 characters long."
                        return render_template(
                            "editprofile.html",
                            user={"username": user[2], "email": user[1]},
                            error=error,
                            message=message
                        )

                    hashed_password = generate_password_hash(new_password)
                    cursor.execute("""
                        UPDATE accounts SET full_name=?, username=?, email=?, password=? WHERE username=?
                    """, (new_name, new_username, new_email, hashed_password, username))

                conn.commit()

            session["username"] = new_username
            session["message"] = "Profile updated successfully!"
            return redirect(url_for("profile"))

        except sqlite3.IntegrityError:
            error = "Username or email already exists."

    return render_template("editprofile.html", user={"username": user[2], "email": user[1]}, error=error, message=message)


@app.route("/add_task", methods=["POST"])
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

@app.route("/edit_task/<int:task_id>", methods=["PUT"])
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

@app.route("/delete_task/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    with sqlite3.connect(TASK_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        conn.commit()
    return jsonify({"success": True})

@app.route("/update_task_status/<int:task_id>", methods=["PUT"])
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

@app.route("/profile")
def profile():
    if "username" not in session:
        session["message"] = "Please log in to view your profile."
        return redirect(url_for("login"))
    username = session["username"]

    # get user info
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT full_name, email, username FROM accounts WHERE username=?", (username,))
        user = cursor.fetchone()
    user_data = {"full_name": user[0], "email": user[1], "username": user[2]}

    # get user's tasks
    with sqlite3.connect(TASK_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE username=? AND status='backlog'", (username,))
        backlog_tasks = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]

        cursor.execute("SELECT * FROM tasks WHERE username=? AND status='in-progress'", (username,))
        in_progress_tasks = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]

        cursor.execute("SELECT * FROM tasks WHERE username=? AND status='completed'", (username,))
        completed_tasks = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]

    return render_template("profile.html",
                           user=user_data,
                           tasks=backlog_tasks,
                           in_progress_tasks=in_progress_tasks,
                           completed_tasks=completed_tasks)

@app.route("/collaboration")
def collaboration():
    if "username" not in session:
        session["message"] = "Please log in first."
        return redirect(url_for("login"))

    username = session["username"]

    # Get user info for the sidebar
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT full_name, email, username FROM accounts WHERE username=?", (username,))
        user = cursor.fetchone()
    
    user_data = {"full_name": user[0], "email": user[1], "username": user[2]}

    with sqlite3.connect(COLLAB_DB) as conn:
        cursor = conn.cursor()

        # Lists created by the user
        cursor.execute("""
            SELECT id, list_name, description FROM collab_lists
            WHERE owner_username = ?
        """, (username,))
        owned_lists = cursor.fetchall()

        # Lists where user is a member (but not owner)
        cursor.execute("""
            SELECT cl.id, cl.list_name, cl.description
            FROM collab_members cm
            JOIN collab_lists cl ON cm.list_id = cl.id
            WHERE cm.member_username = ? AND cl.owner_username != ?
        """, (username, username))
        shared_lists = cursor.fetchall()

    return render_template(
        "collaboration.html",
        user=user_data, 
        username=username,
        owned_lists=owned_lists,
        shared_lists=shared_lists
    )
@app.route("/create_collaboration", methods=["GET", "POST"])
def create_collaboration():
    if "username" not in session:
        session["message"] = "Please log in first."
        return redirect(url_for("login"))
    
    if request.method == "POST":
        list_name = request.form["collab_name"]
        description = request.form["collab_description"]
        members_input = request.form["collab_members"]
        owner_username = session["username"]
        
        # Process members (split by comma and strip whitespace)
        members = [member.strip() for member in members_input.split(",")] if members_input else []
        
        try:
            with sqlite3.connect(COLLAB_DB) as conn:
                cursor = conn.cursor()
                
                # Create the collaboration list
                cursor.execute("""
                    INSERT INTO collab_lists (list_name, description, owner_username)
                    VALUES (?, ?, ?)
                """, (list_name, description, owner_username))
                list_id = cursor.lastrowid
                
                # Add owner as a member
                cursor.execute("""
                    INSERT INTO collab_members (list_id, member_username)
                    VALUES (?, ?)
                """, (list_id, owner_username))
                
                # Add other members if they exist
                for member in members:
                    if member and member != owner_username:  # Don't add duplicate of owner
                        # Check if user exists in accounts
                        with sqlite3.connect(DB_NAME) as accounts_conn:
                            accounts_cursor = accounts_conn.cursor()
                            accounts_cursor.execute("SELECT username FROM accounts WHERE username = ?", (member,))
                            if accounts_cursor.fetchone():
                                cursor.execute("""
                                    INSERT INTO collab_members (list_id, member_username)
                                    VALUES (?, ?)
                                """, (list_id, member))
                
                conn.commit()
            
            session["message"] = f"Collaboration '{list_name}' created successfully!"
            return redirect(url_for("collaboration"))
            
        except sqlite3.Error as e:
            return f"Error creating collaboration: {str(e)}", 500
    
    # FIX: Get user data and pass it to the template
    username = session["username"]
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM accounts WHERE username = ?", (username,))
        user_data = cursor.fetchone()
        
        if user_data:
            # Create a simple user object or dictionary
            user = {"username": user_data[0]}
        else:
            # Fallback if user not found (shouldn't happen if logged in)
            user = {"username": username}
    
    return render_template("createcollab.html", user=user)

@app.route("/collaboration/<int:list_id>")
def view_collaboration(list_id):
    if "username" not in session:
        session["message"] = "Please log in first."
        return redirect(url_for("login"))
    
    username = session["username"]
    
    with sqlite3.connect(COLLAB_DB) as conn:
        cursor = conn.cursor()
        
        # Check if user has access to this collaboration
        cursor.execute("""
            SELECT 1 FROM collab_members 
            WHERE list_id = ? AND member_username = ?
        """, (list_id, username))
        
        if not cursor.fetchone():
            session["message"] = "You don't have access to this collaboration."
            return redirect(url_for("collaboration"))
        
        # Get collaboration details
        cursor.execute("""
            SELECT list_name, description, owner_username 
            FROM collab_lists WHERE id = ?
        """, (list_id,))
        list_info = cursor.fetchone()
        
        if not list_info:
            session["message"] = "Collaboration not found."
            return redirect(url_for("collaboration"))
        
        # Get members
        cursor.execute("""
            SELECT member_username FROM collab_members 
            WHERE list_id = ? ORDER BY joined_at
        """, (list_id,))
        members = [row[0] for row in cursor.fetchall()]
        
        # Get tasks
        cursor.execute("""
            SELECT * FROM collab_tasks 
            WHERE list_id = ? ORDER BY created_at DESC
        """, (list_id,))
        
        tasks = [dict(zip([column[0] for column in cursor.description], row)) 
                for row in cursor.fetchall()]
    
    return render_template("collab_tasks.html",
                         list_id=list_id,
                         list_name=list_info[0],
                         description=list_info[1],
                         owner=list_info[2],
                         members=members,
                         tasks=tasks,
                         username=username)

@app.route("/add_collab_member/<int:list_id>", methods=["POST"])
def add_collab_member(list_id):
    if "username" not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    username = session["username"]
    data = request.get_json()
    new_member = data.get("username")
    
    if not new_member:
        return jsonify({"error": "Username required"}), 400
    
    # Check if current user is the owner
    with sqlite3.connect(COLLAB_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT owner_username FROM collab_lists WHERE id = ?", (list_id,))
        result = cursor.fetchone()
        
        if not result or result[0] != username:
            return jsonify({"error": "Only the owner can add members"}), 403
        
        # Check if new member exists
        with sqlite3.connect(DB_NAME) as accounts_conn:
            accounts_cursor = accounts_conn.cursor()
            accounts_cursor.execute("SELECT username FROM accounts WHERE username = ?", (new_member,))
            if not accounts_cursor.fetchone():
                return jsonify({"error": "User not found"}), 404
        
        # Add member
        try:
            cursor.execute("""
                INSERT INTO collab_members (list_id, member_username)
                VALUES (?, ?)
            """, (list_id, new_member))
            conn.commit()
            
            return jsonify({"success": True, "message": f"Added {new_member} to collaboration"})
        
        except sqlite3.IntegrityError:
            return jsonify({"error": "User is already a member"}), 400

@app.route("/add_collab_task/<int:list_id>", methods=["POST"])
def add_collab_task(list_id):
    if "username" not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    username = session["username"]
    data = request.get_json()
    name = data.get("name")
    priority = data.get("priority")
    date = data.get("date")
    time = data.get("time")
    
    if not name:
        return jsonify({"error": "Task name required"}), 400
    
    # Check if user has access to this collaboration
    with sqlite3.connect(COLLAB_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 1 FROM collab_members 
            WHERE list_id = ? AND member_username = ?
        """, (list_id, username))
        
        if not cursor.fetchone():
            return jsonify({"error": "You don't have access to this collaboration"}), 403
        
        # Add task
        cursor.execute("""
            INSERT INTO collab_tasks (list_id, name, priority, date, time, created_by)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (list_id, name, priority, date, time, username))
        
        task_id = cursor.lastrowid
        conn.commit()
    
    return jsonify({
        "id": task_id, 
        "name": name, 
        "priority": priority, 
        "date": date, 
        "time": time,
        "created_by": username
    })

@app.route("/edit_collab_task/<int:task_id>", methods=["PUT"])
def edit_collab_task(task_id):
    if "username" not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    username = session["username"]
    data = request.get_json()
    name = data.get("name")
    priority = data.get("priority")
    date = data.get("date")
    time = data.get("time")
    
    # Check if user has access to edit this task
    with sqlite3.connect(COLLAB_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ct.list_id FROM collab_tasks ct
            JOIN collab_members cm ON ct.list_id = cm.list_id
            WHERE ct.id = ? AND cm.member_username = ?
        """, (task_id, username))
        
        if not cursor.fetchone():
            return jsonify({"error": "You don't have access to edit this task"}), 403
        
        cursor.execute("""
            UPDATE collab_tasks 
            SET name=?, priority=?, date=?, time=? 
            WHERE id=?
        """, (name, priority, date, time, task_id))
        conn.commit()
    
    return jsonify({"success": True})

@app.route("/delete_collab_task/<int:task_id>", methods=["DELETE"])
def delete_collab_task(task_id):
    if "username" not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    username = session["username"]
    
    # Check if user has access to delete this task
    with sqlite3.connect(COLLAB_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ct.list_id, ct.created_by FROM collab_tasks ct
            JOIN collab_members cm ON ct.list_id = cm.list_id
            WHERE ct.id = ? AND cm.member_username = ?
        """, (task_id, username))
        
        result = cursor.fetchone()
        if not result:
            return jsonify({"error": "You don't have access to delete this task"}), 403
        
        # Allow deletion if user created the task or is the list owner
        list_id = result[0]
        created_by = result[1]
        
        cursor.execute("SELECT owner_username FROM collab_lists WHERE id = ?", (list_id,))
        owner = cursor.fetchone()[0]
        
        if username != created_by and username != owner:
            return jsonify({"error": "Only task creator or list owner can delete tasks"}), 403
        
        cursor.execute("DELETE FROM collab_tasks WHERE id=?", (task_id,))
        conn.commit()
    
    return jsonify({"success": True})

@app.route("/update_collab_task_status/<int:task_id>", methods=["PUT"])
def update_collab_task_status(task_id):
    if "username" not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    username = session["username"]
    data = request.get_json()
    status = data.get("status")
    
    if status not in ["backlog", "in-progress", "completed"]:
        return jsonify({"success": False, "error": "Invalid status"})
    
    # Check if user has access to this task
    with sqlite3.connect(COLLAB_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 1 FROM collab_tasks ct
            JOIN collab_members cm ON ct.list_id = cm.list_id
            WHERE ct.id = ? AND cm.member_username = ?
        """, (task_id, username))
        
        if not cursor.fetchone():
            return jsonify({"error": "You don't have access to this task"}), 403
        
        cursor.execute("UPDATE collab_tasks SET status=? WHERE id=?", (status, task_id))
        conn.commit()
    
    return jsonify({"success": True})

@app.route("/get_collab_lists")
def get_collab_lists():
    if "username" not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    username = session["username"]
    
    with sqlite3.connect(COLLAB_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT cl.id, cl.list_name, cl.description 
            FROM collab_lists cl
            JOIN collab_members cm ON cl.id = cm.list_id
            WHERE cm.member_username = ?
        """, (username,))
        lists = cursor.fetchall()
    
    return jsonify([{"id": row[0], "name": row[1], "description": row[2]} for row in lists])

if __name__ == "__main__":
    init_db()
    init_tasks_db()
    init_collaborations_db()
    app.run(debug=True)
