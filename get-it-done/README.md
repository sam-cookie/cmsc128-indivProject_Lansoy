This project supports user authentication, personal to do list in which you can add, edit, delete tasks, and you can also collab with other people.

Backend: Python + Flask
Database: SQLite (stored locally as accounts.db, collaborations.db, and tododatabase)
Frontend: HTML, CSS, JavaSctipt

Prerequisites
Python 3.x, Flask, SQLite (usually included with Python)

To run the web app:
Clone or download this project. Ensure all frontend files (html and CSS) and backend file (accounts.db) are in the same directory. Start the server with: py app.py

Open your browser and go to: http://127.0.0.1:5000 or whichever is provided to you.

API ENDPOINTS

User Login
Method - Endpoint - Description
GET - /login - shows the login page  
POST - /login - verifies username & password  
GET - /register - shows the registration page  
POST - /register - creates a new account  
GET - /profile/<username> - displays the user’s profile  
GET/POST - /editprofile/<username> - edits profile info  
GET/POST - /forgotpassword - verifies security answer  
GET/POST - /editpassword/<username> - allows password reset  

Collaboration Features
GET /collaboration - Display collaborative lists dashboard
GET/POST /create_collaboration - Create new collaborative list
GET /collaboration/<list_id> - View collaboration details and tasks
POST /add_collab_member/<list_id> - Add member to list
POST /add_collab_task/<list_id> - Add task to list
PUT /edit_collab_task/<task_id> - Edit task details
DELETE /delete_collab_task/<task_id> - Remove task
PUT /update_collab_task_status/<task_id> - Update task status
GET /get_collab_lists - Get lists data (JSON)

Request/Response Examples
Add Task
POST /add_task
Request Body (JSON):
{ "name": "Finish project", "priority": "high", "date": "2025-09-30", "time": "14:00" }
Response:
{ "id": 1, "name": "Finish project", "priority": "high", "date": "2025-09-30", "time": "14:00" }

Edit Task
PUT /edit_task/<task_id>
Request Body (JSON):
{ "name": "Submit project", "priority": "mid", "date": "2025-10-01", "time": "16:00" }
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