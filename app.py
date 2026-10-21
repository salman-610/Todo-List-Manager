
import os
from datetime import datetime
from uuid import uuid4

from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash
from mysql.connector import Error, IntegrityError

from db import get_db_connection

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

if not app.secret_key:
    raise RuntimeError(
        "FLASK_SECRET_KEY is missing. Check your .env file."
    )

VALID_STATUSES = ["Pending", "In Progress", "Completed"]
VALID_PRIORITIES = ["Low", "Medium", "High", "Urgent"]


def open_database():
    try:
        return get_db_connection()
    except Error:
        app.logger.exception("MySQL connection failed")
        return None


def database_error_message():
    return "A database error occurred. Please check the VS Code terminal."


def empty_chart_data():
    return {
        "total_tasks": 0,
        "completed": 0,
        "urgent": {"pending": 0, "in_progress": 0},
        "high": {"pending": 0, "in_progress": 0},
        "medium": {"pending": 0, "in_progress": 0},
        "low": {"pending": 0, "in_progress": 0}
    }


def validate_task_form(form):
    title = form.get("title", "").strip()
    description = form.get("description", "").strip()
    created_by = form.get("created_by", "").strip()
    assigned_to = form.get("assigned_to", "").strip()
    priority = form.get("priority", "").strip()
    status = form.get("status", "").strip()
    due_date_text = form.get("due_date", "").strip()

    if not title or not created_by or not assigned_to:
        return None, "Title, Created By, and Assigned To are required."

    if len(title) > 150:
        return None, "Task title must not exceed 150 characters."

    if len(created_by) > 100 or len(assigned_to) > 100:
        return None, "Created By and Assigned To must not exceed 100 characters."

    if priority not in VALID_PRIORITIES:
        return None, "Please select a valid priority."

    if status not in VALID_STATUSES:
        return None, "Please select a valid initial status."

    if not due_date_text:
        return None, "Due Date is required."

    try:
        due_date = datetime.strptime(due_date_text, "%Y-%m-%dT%H:%M")
    except ValueError:
        return None, "Please enter a valid due date and time."

    return {
        "title": title,
        "description": description or None,
        "created_by": created_by,
        "assigned_to": assigned_to,
        "priority": priority,
        "status": status,
        "due_date": due_date
    }, None


def get_completed_at(new_status, old_status=None, old_completed_at=None):
    """
    Completed tasks get a timestamp.
    Existing completion timestamps are preserved when appropriate.
    Other statuses always have a NULL completion timestamp.
    """
    if new_status != "Completed":
        return None

    if old_status == "Completed" and old_completed_at is not None:
        return old_completed_at

    return datetime.now()


@app.route("/")
def home():
    status_filter = request.args.get("status", "").strip()
    priority_filter = request.args.get("priority", "").strip()
    assigned_filter = request.args.get("assigned_to", "").strip()
    created_by_filter = request.args.get("created_by", "").strip()
    search_query = request.args.get("search", "").strip()[:150]
    sort_by = request.args.get("sort", "oldest").strip()

    if status_filter not in VALID_STATUSES:
        status_filter = ""

    if priority_filter not in VALID_PRIORITIES:
        priority_filter = ""

    valid_sort_options = ["oldest", "newest", "priority", "due_date", "title"]

    if sort_by not in valid_sort_options:
        sort_by = "oldest"

    empty_stats = {
        "total_tasks": 0,
        "pending_tasks": 0,
        "in_progress_tasks": 0,
        "completed_tasks": 0,
        "urgent_tasks": 0
    }

    chart_data = empty_chart_data()
    connection = open_database()

    if connection is None:
        flash(database_error_message(), "error")
        return render_template(
            "index.html", tasks=[], stats=empty_stats,
            chart_data=chart_data, team_members=[], task_creators=[],
            status_filter=status_filter, priority_filter=priority_filter,
            assigned_filter=assigned_filter, created_by_filter=created_by_filter,
            search_query=search_query, sort_by=sort_by
        ), 503

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                COUNT(*) AS total_tasks,
                COALESCE(SUM(status = 'Pending'), 0) AS pending_tasks,
                COALESCE(SUM(status = 'In Progress'), 0) AS in_progress_tasks,
                COALESCE(SUM(status = 'Completed'), 0) AS completed_tasks,
                COALESCE(SUM(
                    priority = 'Urgent'
                    AND status IN ('Pending', 'In Progress')
                ), 0) AS urgent_tasks
            FROM tasks
        """)
        stats = cursor.fetchone()

        cursor.execute("""
            SELECT
                COUNT(*) AS total_tasks,
                COALESCE(SUM(status = 'Completed'), 0) AS completed,
                COALESCE(SUM(priority = 'Urgent' AND status = 'Pending'), 0) AS urgent_pending,
                COALESCE(SUM(priority = 'Urgent' AND status = 'In Progress'), 0) AS urgent_in_progress,
                COALESCE(SUM(priority = 'High' AND status = 'Pending'), 0) AS high_pending,
                COALESCE(SUM(priority = 'High' AND status = 'In Progress'), 0) AS high_in_progress,
                COALESCE(SUM(priority = 'Medium' AND status = 'Pending'), 0) AS medium_pending,
                COALESCE(SUM(priority = 'Medium' AND status = 'In Progress'), 0) AS medium_in_progress,
                COALESCE(SUM(priority = 'Low' AND status = 'Pending'), 0) AS low_pending,
                COALESCE(SUM(priority = 'Low' AND status = 'In Progress'), 0) AS low_in_progress
            FROM tasks
        """)
        counts = cursor.fetchone()

        chart_data = {
            "total_tasks": int(counts["total_tasks"] or 0),
            "completed": int(counts["completed"] or 0),
            "urgent": {
                "pending": int(counts["urgent_pending"] or 0),
                "in_progress": int(counts["urgent_in_progress"] or 0)
            },
            "high": {
                "pending": int(counts["high_pending"] or 0),
                "in_progress": int(counts["high_in_progress"] or 0)
            },
            "medium": {
                "pending": int(counts["medium_pending"] or 0),
                "in_progress": int(counts["medium_in_progress"] or 0)
            },
            "low": {
                "pending": int(counts["low_pending"] or 0),
                "in_progress": int(counts["low_in_progress"] or 0)
            }
        }

        cursor.execute("""
            SELECT DISTINCT TRIM(assigned_to) AS assigned_to
            FROM tasks
            WHERE assigned_to IS NOT NULL AND TRIM(assigned_to) != ''
            ORDER BY assigned_to
        """)
        team_members = cursor.fetchall()

        cursor.execute("""
            SELECT DISTINCT TRIM(created_by) AS created_by
            FROM tasks
            WHERE created_by IS NOT NULL AND TRIM(created_by) != ''
            ORDER BY created_by
        """)
        task_creators = cursor.fetchall()

        query = "SELECT * FROM tasks WHERE 1 = 1"
        values = []

        if status_filter:
            query += " AND status = %s"
            values.append(status_filter)

        if priority_filter:
            query += " AND priority = %s"
            values.append(priority_filter)

        if assigned_filter:
            query += " AND assigned_to = %s"
            values.append(assigned_filter)

        if created_by_filter:
            query += " AND TRIM(created_by) = %s"
            values.append(created_by_filter)

        if search_query:
            query += """
                AND (task_number LIKE %s OR title LIKE %s OR description LIKE %s)
            """
            search_value = f"%{search_query}%"
            values.extend([search_value, search_value, search_value])

        sort_options = {
            "oldest": "id ASC",
            "newest": "id DESC",
            "priority": """
                CASE priority
                    WHEN 'Urgent' THEN 1
                    WHEN 'High' THEN 2
                    WHEN 'Medium' THEN 3
                    WHEN 'Low' THEN 4
                END ASC, id DESC
            """,
            "due_date": "due_date IS NULL ASC, due_date ASC, id DESC",
            "title": "title ASC"
        }

        query += " ORDER BY " + sort_options[sort_by]
        cursor.execute(query, tuple(values))
        tasks = cursor.fetchall()

        for index, task in enumerate(tasks, start=1):
            task["serial_number"] = index

        return render_template(
            "index.html", tasks=tasks, stats=stats,
            chart_data=chart_data, team_members=team_members,
            task_creators=task_creators, status_filter=status_filter,
            priority_filter=priority_filter, assigned_filter=assigned_filter,
            created_by_filter=created_by_filter, search_query=search_query,
            sort_by=sort_by
        )

    except Error:
        app.logger.exception("Failed to load tasks from MySQL")
        flash(database_error_message(), "error")
        return render_template(
            "index.html", tasks=[], stats=empty_stats,
            chart_data=empty_chart_data(), team_members=[], task_creators=[],
            status_filter=status_filter, priority_filter=priority_filter,
            assigned_filter=assigned_filter, created_by_filter=created_by_filter,
            search_query=search_query, sort_by=sort_by
        ), 500

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


@app.route("/add_task", methods=["POST"])
def add_task():
    data, validation_error = validate_task_form(request.form)

    if validation_error:
        flash(validation_error, "error")
        return redirect(url_for("home"))

    connection = open_database()

    if connection is None:
        flash(database_error_message(), "error")
        return redirect(url_for("home"))

    cursor = None

    try:
        cursor = connection.cursor()
        temporary_number = "TMP" + uuid4().hex[:16]
        completed_at = get_completed_at(data["status"])

        cursor.execute("""
            INSERT INTO tasks (
                task_number, title, description, status, created_by,
                assigned_to, priority, due_date, completed_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            temporary_number, data["title"], data["description"],
            data["status"], data["created_by"], data["assigned_to"],
            data["priority"], data["due_date"], completed_at
        ))

        task_id = cursor.lastrowid
        task_number = f"TD{task_id:03d}L"

        cursor.execute(
            "UPDATE tasks SET task_number = %s WHERE id = %s",
            (task_number, task_id)
        )

        connection.commit()
        flash(f"Task {task_number} created successfully!", "success")

    except IntegrityError:
        connection.rollback()
        app.logger.exception("Task insert failed due to a database constraint")
        flash("The task could not be saved. Check the VS Code terminal.", "error")

    except Error:
        connection.rollback()
        app.logger.exception("MySQL error while creating a task")
        flash(database_error_message(), "error")

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()

    return redirect(url_for("home"))


@app.route("/update_status/<int:task_id>", methods=["POST"])
def update_status(task_id):
    new_status = request.form.get("status", "").strip()

    if new_status not in VALID_STATUSES:
        flash("Please select a valid status.", "error")
        return redirect(url_for("home"))

    connection = open_database()

    if connection is None:
        flash(database_error_message(), "error")
        return redirect(url_for("home"))

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT status, completed_at
            FROM tasks
            WHERE id = %s
        """, (task_id,))

        existing_task = cursor.fetchone()

        if existing_task is None:
            flash("Task not found. It may have already been deleted.", "error")
            return redirect(url_for("home"))

        completed_at = get_completed_at(
            new_status,
            existing_task["status"],
            existing_task["completed_at"]
        )

        cursor.execute("""
            UPDATE tasks
            SET status = %s,
                completed_at = %s
            WHERE id = %s
        """, (new_status, completed_at, task_id))

        connection.commit()
        flash("Task status updated successfully!", "success")

    except Error:
        connection.rollback()
        app.logger.exception("Failed to update task status")
        flash(database_error_message(), "error")

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()

    return redirect(url_for("home"))


@app.route("/edit_task/<int:task_id>", methods=["POST"])
def edit_task(task_id):
    data, validation_error = validate_task_form(request.form)

    if validation_error:
        flash(validation_error, "error")
        return redirect(url_for("home"))

    connection = open_database()

    if connection is None:
        flash(database_error_message(), "error")
        return redirect(url_for("home"))

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT status, completed_at
            FROM tasks
            WHERE id = %s
        """, (task_id,))

        existing_task = cursor.fetchone()

        if existing_task is None:
            flash("Task not found. It may have already been deleted.", "error")
            return redirect(url_for("home"))

        completed_at = get_completed_at(
            data["status"],
            existing_task["status"],
            existing_task["completed_at"]
        )

        cursor.execute("""
            UPDATE tasks
            SET title = %s,
                description = %s,
                created_by = %s,
                assigned_to = %s,
                priority = %s,
                due_date = %s,
                status = %s,
                completed_at = %s
            WHERE id = %s
        """, (
            data["title"],
            data["description"],
            data["created_by"],
            data["assigned_to"],
            data["priority"],
            data["due_date"],
            data["status"],
            completed_at,
            task_id
        ))

        connection.commit()
        flash("Task updated successfully!", "success")

    except Error:
        connection.rollback()
        app.logger.exception("MySQL error while editing a task")
        flash(database_error_message(), "error")

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()

    return redirect(url_for("home"))


@app.route("/delete_task/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    connection = open_database()

    if connection is None:
        flash(database_error_message(), "error")
        return redirect(url_for("home"))

    cursor = None

    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))

        if cursor.rowcount == 0:
            flash("Task not found. It may have already been deleted.", "error")
        else:
            connection.commit()
            flash("Task deleted successfully!", "success")

    except Error:
        connection.rollback()
        app.logger.exception("MySQL error while deleting a task")
        flash(database_error_message(), "error")

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()

    return redirect(url_for("home"))


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode)
