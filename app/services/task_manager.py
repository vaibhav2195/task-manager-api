from typing import List, Optional
from app.exceptions import TaskNotFoundError
from app.models.task import Task, TaskPriority
from app.repositories.base import BaseTaskRepository


class TaskManager:
    """Service class managing Task CRUD logic and business rules."""

    def __init__(self, repository: BaseTaskRepository):
        self.repository = repository

    def create_task(
        self,
        title: str,
        description: Optional[str] = "",
        priority: Optional[str] = TaskPriority.MEDIUM,
    ) -> Task:
        task = Task(title=title, description=description, priority=priority)
        return self.repository.create(task)

    def get_task_by_id(self, task_id: str) -> Task:
        task = self.repository.get_by_id(task_id)
        if not task:
            raise TaskNotFoundError(task_id)
        return task

    def list_tasks(
        self, completed: Optional[bool] = None, limit: int = 100, offset: int = 0
    ) -> List[Task]:
        return self.repository.get_all(completed=completed, limit=limit, offset=offset)

    def update_task(
        self,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        completed: Optional[bool] = None,
        priority: Optional[str] = None,
    ) -> Task:
        task = self.get_task_by_id(task_id)
        task.update(
            title=title,
            description=description,
            completed=completed,
            priority=priority,
        )
        return self.repository.update(task)

    def delete_task(self, task_id: str) -> bool:
        task = self.get_task_by_id(task_id)
        return self.repository.delete(task.id)

    def get_task_count(self) -> int:
        return self.repository.count()
