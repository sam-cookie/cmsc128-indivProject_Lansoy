This project is a user account management that is yet to be incorporated with the todolist built with flask and sqlite.
It supports registration, login, password reset using a security question, and profile editing — all without javascript.

Frontend: HTML and CSS Backend: Python + Flask. Database: SQLite (stored locally as accounts.db).

To use the web app, make sure to install the following: Python 3.x Flask SQLite

To run the web app:
Clone or download this project. Ensure all frontend files (html and CSS) and backend file (accounts.db) are in the same directory. Start the server with: python accounts.py

Open your browser and go to: http://127.0.0.1:5000 or whichever is provided to you.

API ENDPOINTS

Method - Endpoint - Description
GET - /login - shows the login page  
POST - /login - verifies username & password  
GET - /register - shows the registration page  
POST - /register - creates a new account  
GET - /profile/<username> - displays the user’s profile  
GET/POST - /editprofile/<username> - edits profile info  
GET/POST - /forgotpassword - verifies security answer  
GET/POST - /editpassword/<username> - allows password reset  

First part of the lab was in collabaration with Eleah Joy Melchor