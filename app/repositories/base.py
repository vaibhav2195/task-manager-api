from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.task import Task


class BaseTaskRepository(ABC):
    """Abstract Base Class for Task Repository Pattern."""

    @abstractmethod
    def create(self, task: Task) -> Task:
        """Save a new task to storage."""
        pass

    @abstractmethod
    def get_by_id(self, task_id: str) -> Optional[Task]:
        """Retrieve a task by its unique ID."""
        pass

    @abstractmethod
    def get_all(
        self, completed: Optional[bool] = None, limit: int = 100, offset: int = 0
    ) -> List[Task]:
        """Retrieve all tasks with optional filtering and pagination."""
        pass

    @abstractmethod
    def update(self, task: Task) -> Task:
        """Update an existing task in storage."""
        pass

    @abstractmethod
    def delete(self, task_id: str) -> bool:
        """Delete a task by ID. Returns True if deleted, False if not found."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Get total number of tasks stored."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all tasks (used primarily for testing)."""
        pass
