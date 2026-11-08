 Team To-Do List Manager

A web-based task management application built using Python, Flask, and MySQL. The application enables teams to create, assign, prioritize, and track tasks through a centralized dashboard.

 Features

- Task creation, editing, and deletion.
- Unique task reference number generation.
- Task assignment and ownership tracking.
- Status and priority management.
- Due date and completion timestamp tracking.
- Dashboard with task statistics and visual analytics.
- Search, filtering, and sorting functionality.

 Tech Stack

- Backend: Python, Flask
- Database: MySQL
- Frontend: HTML, CSS, JavaScript
- Database Connector: MySQL Connector/Python
- Configuration: Python-dotenv
- Version Control: Git, GitHub

 Project Structure


to_do_app/
├── static/
│   └── style.css
├── templates/
│   └── index.html
├── app.py
├── db.py
├── database.sql
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md


 Setup and Execution

 Prerequisites

- Python
- MySQL Server
- Git

 1. Clone the Repository


git clone https://github.com/salman-610/Todo-List-Manager.git
cd Todo-List-Manager


 2. Install Dependencies


python -m venv .venv
python -m pip install -r requirements.txt


Activate the virtual environment before running the application.

 3. Database Setup

Execute 'database.sql' against your MySQL Server.

The script initializes the 'todo_db' database and creates the 'tasks' table with the required columns, constraints, default values, and indexes.

 4. Environment Configuration

Create a '.env' file using '.env.example' as a template and configure the database credentials and Flask secret key.

 5. Run the Application


python app.py


Application URL: 'http://127.0.0.1:5000/'

 Database Schema

 tasks

Stores task identifiers, descriptions, ownership details, status, priority, creation timestamp, due date, and completion timestamp.

 Configuration Notes

- Database credentials and application settings are managed through environment variables.
- 'database.sql' provides reproducible database initialization.
- Sensitive configuration files and virtual environments are excluded from version control.

 Author

Salman