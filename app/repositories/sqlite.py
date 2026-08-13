from datetime import datetime
import sqlite3
from typing import List, Optional
from app.exceptions import DuplicateTaskError, RepositoryError, TaskNotFoundError
from app.models.task import Task
from app.repositories.base import BaseTaskRepository


class SQLiteTaskRepository(BaseTaskRepository):
    """Class-based SQLite implementation of Task Repository."""

    def __init__(self, db_path: str = "tasks.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            raise RepositoryError(f"Failed to connect to SQLite database: {e}")

    def _init_db(self) -> None:
        """Initialize the tasks table if it does not exist."""
        sql = """
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            completed BOOLEAN NOT NULL DEFAULT 0,
            priority TEXT NOT NULL DEFAULT 'medium',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """
        try:
            with self._get_connection() as conn:
                conn.execute(sql)
                conn.commit()
        except sqlite3.Error as e:
            raise RepositoryError(f"Database initialization failed: {e}")

    def _row_to_task(self, row: sqlite3.Row) -> Task:
        return Task(
            task_id=row["id"],
            title=row["title"],
            description=row["description"],
            completed=bool(row["completed"]),
            priority=row["priority"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def create(self, task: Task) -> Task:
        sql = """
        INSERT INTO tasks (id, title, description, completed, priority, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        try:
            with self._get_connection() as conn:
                conn.execute(
                    sql,
                    (
                        task.id,
                        task.title,
                        task.description,
                        int(task.completed),
                        task.priority,
                        task.created_at.isoformat(),
                        task.updated_at.isoformat(),
                    ),
                )
                conn.commit()
            return task
        except sqlite3.IntegrityError:
            raise DuplicateTaskError(task.id)
        except sqlite3.Error as e:
            raise RepositoryError(f"Error creating task: {e}")

    def get_by_id(self, task_id: str) -> Optional[Task]:
        sql = "SELECT * FROM tasks WHERE id = ?"
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (task_id,))
                row = cursor.fetchone()
                if row:
                    return self._row_to_task(row)
                return None
        except sqlite3.Error as e:
            raise RepositoryError(f"Error fetching task by ID: {e}")

    def get_all(
        self, completed: Optional[bool] = None, limit: int = 100, offset: int = 0
    ) -> List[Task]:
        params = []
        sql = "SELECT * FROM tasks"
        if completed is not None:
            sql += " WHERE completed = ?"
            params.append(int(completed))

        sql += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, params)
                rows = cursor.fetchall()
                return [self._row_to_task(r) for r in rows]
        except sqlite3.Error as e:
            raise RepositoryError(f"Error fetching tasks: {e}")

    def update(self, task: Task) -> Task:
        sql = """
        UPDATE tasks
        SET title = ?, description = ?, completed = ?, priority = ?, updated_at = ?
        WHERE id = ?
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    sql,
                    (
                        task.title,
                        task.description,
                        int(task.completed),
                        task.priority,
                        task.updated_at.isoformat(),
                        task.id,
                    ),
                )
                if cursor.rowcount == 0:
                    raise TaskNotFoundError(task.id)
                conn.commit()
            return task
        except TaskNotFoundError:
            raise
        except sqlite3.Error as e:
            raise RepositoryError(f"Error updating task: {e}")

    def delete(self, task_id: str) -> bool:
        sql = "DELETE FROM tasks WHERE id = ?"
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (task_id,))
                deleted = cursor.rowcount > 0
                conn.commit()
                return deleted
        except sqlite3.Error as e:
            raise RepositoryError(f"Error deleting task: {e}")

    def count(self) -> int:
        sql = "SELECT COUNT(*) FROM tasks"
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                return cursor.fetchone()[0]
        except sqlite3.Error as e:
            raise RepositoryError(f"Error counting tasks: {e}")

    def clear(self) -> None:
        sql = "DELETE FROM tasks"
        try:
            with self._get_connection() as conn:
                conn.execute(sql)
                conn.commit()
        except sqlite3.Error as e:
            raise RepositoryError(f"Error clearing tasks table: {e}")
