To-do-list App

By Samantha Lodenn D. Lansoy 

This project is a simple To-do-list web application that allows users to create, update, and manage tasks.

Frontend: HTML, CSS, JavaScript (with Font Awesome icons for styling).
Backend: Python + Flask.
Database: SQLite (stored locally as tododatabase.db).

The app supports task creation with priority, date, and time, as well as task status updates (backlog, in-progress, completed).

To use the web app, make sure to install the following:
Python 3.x
Flask
SQLite

To run the web app:  
Clone or download this project.
Ensure all frontend files (index.html, CSS, JS) and backend file (todolist.py) are in the same directory.
Start the server with:
python todolist.py

Open your browser and go to:
http://127.0.0.1:5000 or whichever is provided to you.

API Endpoints

The backend provides JSON API endpoints for interacting with the database. This helps the frontend communicate with the backend
to make the user see the changes without reloading.

Add Task

POST /add_task

Request Body (JSON):

{
  "name": "Finish project",
  "priority": "high",
  "date": "2025-09-30",
  "time": "14:00"
}


Response:

{
  "id": 1,
  "name": "Finish project",
  "priority": "high",
  "date": "2025-09-30",
  "time": "14:00"
}

Edit Task

PUT /edit_task/<task_id>

Request Body (JSON):

{
  "name": "Submit project",
  "priority": "mid",
  "date": "2025-10-01",
  "time": "16:00"
}


Response:

{ "success": true }

Delete Task

DELETE /delete_task/<task_id>

Response:

{ "success": true }

Update Task Status

PUT /update_task_status/<task_id>

Request Body (JSON):

{ "status": "completed" }


Response:

{ "success": true }

First part of the lab was in collabaration with Eleah Joy Melchor
