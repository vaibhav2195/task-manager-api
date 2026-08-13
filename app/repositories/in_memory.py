from threading import Lock
from typing import Dict, List, Optional
from app.exceptions import DuplicateTaskError, TaskNotFoundError
from app.models.task import Task
from app.repositories.base import BaseTaskRepository


class InMemoryTaskRepository(BaseTaskRepository):
    """In-memory thread-safe implementation of Task Repository."""

    def __init__(self):
        self._storage: Dict[str, Task] = {}
        self._lock = Lock()

    def create(self, task: Task) -> Task:
        with self._lock:
            if task.id in self._storage:
                raise DuplicateTaskError(task.id)
            self._storage[task.id] = task
            return task

    def get_by_id(self, task_id: str) -> Optional[Task]:
        with self._lock:
            return self._storage.get(task_id)

    def get_all(
        self, completed: Optional[bool] = None, limit: int = 100, offset: int = 0
    ) -> List[Task]:
        with self._lock:
            tasks = list(self._storage.values())
            if completed is not None:
                tasks = [t for t in tasks if t.completed == completed]
            # Sort by created_at descending
            tasks.sort(key=lambda x: x.created_at, reverse=True)
            return tasks[offset : offset + limit]

    def update(self, task: Task) -> Task:
        with self._lock:
            if task.id not in self._storage:
                raise TaskNotFoundError(task.id)
            self._storage[task.id] = task
            return task

    def delete(self, task_id: str) -> bool:
        with self._lock:
            if task_id in self._storage:
                del self._storage[task_id]
                return True
            return False

    def count(self) -> int:
        with self._lock:
            return len(self._storage)

    def clear(self) -> None:
        with self._lock:
            self._storage.clear()
