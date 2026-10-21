# To-Do List Manager

A web-based task management application built using Python, Flask, and MySQL. It helps users create, organize, track, and manage team tasks through a simple dashboard.

## Features

- Create, edit, and delete tasks
- Assign tasks to team members
- Track task status: Pending, In Progress, and Completed
- Set task priorities: Low, Medium, High, and Urgent
- Set due dates and times
- Automatically record task completion timestamps
- Dashboard with task statistics
- Visual chart showing task status and priority
- Search tasks by task number, title, or description
- Filter tasks by status, priority, creator, and assignee
- Sort tasks by creation order, priority, due date, or title
- Store task information in a MySQL database

## Technologies Used

- **Python** — application logic
- **Flask** — web framework
- **MySQL** — relational database
- **mysql-connector-python** — Python-to-MySQL connection
- **HTML and CSS** — user interface
- **python-dotenv** — environment variable configuration

## Project Structure

```text
to_do_app/
├── app.py
├── db.py
├── requirements.txt
├── .gitignore
├── .env
├── templates/
│   └── index.html
└── static/
```

The `.env` file and `.venv/` directory are local files and should not be committed to GitHub.

## Prerequisites

- Python installed
- MySQL Server installed and running
- Git installed (for GitHub upload)

## Setup and Installation

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd to_do_app
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows Command Prompt:

```bat
.venv\Scripts\activate.bat
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create the MySQL database

Open MySQL Workbench and execute:

```sql
CREATE DATABASE todo_db;
USE todo_db;
```

Create the `tasks` table using the schema documented for this project.

### 5. Configure environment variables

Create a `.env` file in the project root. Add your own local database credentials and a newly generated Flask secret key:

```text
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=todo_db
FLASK_SECRET_KEY=your_new_secret_key
```

Use the variable names expected by your `db.py` file. Never commit `.env` or publish passwords and secret keys.

### 6. Run the application

```bash
python app.py
```

Open the local address displayed in your terminal, typically:

```text
http://127.0.0.1:5000
```

## Database

The application uses MySQL to store tasks, task numbers, descriptions, creators, assignees, priorities, statuses, due dates, creation timestamps, and completion timestamps.

## Future Improvements

- User authentication
- Deployment to a hosting platform
- Automated tests

## Author

Python development project created as part of a hands-on Python project portfolio.
