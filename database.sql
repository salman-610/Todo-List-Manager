CREATE DATABASE IF NOT EXISTS todo_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE todo_db;

CREATE TABLE IF NOT EXISTS tasks (

    -- Unique auto-incrementing database ID
    id INT AUTO_INCREMENT PRIMARY KEY,

    -- Custom task reference number (example: TD001L)
    task_number VARCHAR(20) NOT NULL UNIQUE,


    title VARCHAR(150) NOT NULL,
    description TEXT,


    status ENUM(
        'Pending',
        'In Progress',
        'Completed'
    ) NOT NULL DEFAULT 'Pending',


    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    created_by VARCHAR(100) NOT NULL,
    assigned_to VARCHAR(100) NOT NULL,

    priority ENUM(
        'Low',
        'Medium',
        'High',
        'Urgent'
    ) NOT NULL DEFAULT 'Medium',

    -- Due date and completion timestamp
    due_date DATETIME NOT NULL,
    completed_at DATETIME DEFAULT NULL

)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci;



CREATE INDEX idx_tasks_status
ON tasks (status);

CREATE INDEX idx_tasks_priority
ON tasks (priority);

CREATE INDEX idx_tasks_assigned_to
ON tasks (assigned_to);

CREATE INDEX idx_tasks_created_by
ON tasks (created_by);

CREATE INDEX idx_tasks_due_date
ON tasks (due_date);


SHOW DATABASES LIKE 'todo_db';

USE todo_db;

SHOW TABLES;

DESCRIBE tasks;

SELECT COUNT(*) AS total_tasks
FROM tasks;


