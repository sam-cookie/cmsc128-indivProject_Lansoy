from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
import sqlite3

collab_bp = Blueprint('collaboration', __name__)

# DB files
DB_NAME = "accounts.db"
COLLAB_DB = "collaborations.db"

@collab_bp.route("/collaboration")
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

        # lists created by the user
        cursor.execute("""
            SELECT id, list_name, description FROM collab_lists
            WHERE owner_username = ?
        """, (username,))
        owned_lists = cursor.fetchall()

        # lists where user is a member
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

@collab_bp.route("/create_collaboration", methods=["GET", "POST"])
def create_collaboration():
    if "username" not in session:
        session["message"] = "Please log in first."
        return redirect(url_for("login"))
    
    if request.method == "POST":
        list_name = request.form["collab_name"]
        description = request.form["collab_description"]
        members_input = request.form["collab_members"]
        owner_username = session["username"]

        members = [member.strip() for member in members_input.split(",")] if members_input else []
        
        try:
            with sqlite3.connect(COLLAB_DB) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO collab_lists (list_name, description, owner_username)
                    VALUES (?, ?, ?)
                """, (list_name, description, owner_username))
                list_id = cursor.lastrowid
                
                # adding owner as a member
                cursor.execute("""
                    INSERT INTO collab_members (list_id, member_username)
                    VALUES (?, ?)
                """, (list_id, owner_username))
                
                #checker
                for member in members:
                    if member and member != owner_username:  
                        with sqlite3.connect(DB_NAME) as accounts_conn:
                            accounts_cursor = accounts_conn.cursor()
                            accounts_cursor.execute("SELECT username FROM accounts WHERE username = ?", (member,))
                            if accounts_cursor.fetchone():
                                cursor.execute("""
                                    INSERT INTO collab_members (list_id, member_username)
                                    VALUES (?, ?)
                                """, (list_id, member))
                            else: 
                                print(f"User '{member}' does not exist. Skipping.")
                
                conn.commit()
            
            session["message"] = f"Collaboration '{list_name}' created successfully!"
            return redirect(url_for("collaboration.collaboration"))
            
        except sqlite3.Error as e:
            return f"Error creating collaboration: {str(e)}", 500
    
    username = session["username"]
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM accounts WHERE username = ?", (username,))
        user_data = cursor.fetchone()
        
        if user_data:
            user = {"username": user_data[0]}
        else:
            user = {"username": username}
    
    return render_template("createcollab.html", user=user)

@collab_bp.route("/collaboration/<int:list_id>")
def view_collaboration(list_id):
    if "username" not in session:
        session["message"] = "Please log in first."
        return redirect(url_for("login"))
    
    username = session["username"]
    
    with sqlite3.connect(COLLAB_DB) as conn:
        cursor = conn.cursor()
        
        # check if user has access to this collaboration
        cursor.execute("""
            SELECT 1 FROM collab_members 
            WHERE list_id = ? AND member_username = ?
        """, (list_id, username))
        
        if not cursor.fetchone():
            session["message"] = "You don't have access to this collaboration."
            return redirect(url_for("collaboration.collaboration"))
        
        # get collaboration details
        cursor.execute("""
            SELECT list_name, description, owner_username 
            FROM collab_lists WHERE id = ?
        """, (list_id,))
        list_info = cursor.fetchone()
        
        if not list_info:
            session["message"] = "Collaboration not found."
            return redirect(url_for("collaboration.collaboration"))
        
        # get members
        cursor.execute("""
            SELECT member_username FROM collab_members 
            WHERE list_id = ? ORDER BY joined_at
        """, (list_id,))
        members = [row[0] for row in cursor.fetchall()]
        
        # get tasks
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

@collab_bp.route("/add_collab_member/<int:list_id>", methods=["POST"])
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

@collab_bp.route("/add_collab_task/<int:list_id>", methods=["POST"])
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

@collab_bp.route("/edit_collab_task/<int:task_id>", methods=["PUT"])
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

@collab_bp.route("/delete_collab_task/<int:task_id>", methods=["DELETE"])
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

@collab_bp.route("/update_collab_task_status/<int:task_id>", methods=["PUT"])
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

@collab_bp.route("/get_collab_lists")
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