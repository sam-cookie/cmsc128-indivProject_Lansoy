import sqlite3
import os

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