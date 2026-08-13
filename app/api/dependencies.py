from functools import lru_cache
from fastapi import Depends
from app.config import settings
from app.repositories.base import BaseTaskRepository
from app.repositories.in_memory import InMemoryTaskRepository
from app.repositories.sqlite import SQLiteTaskRepository
from app.services.task_manager import TaskManager


@lru_cache()
def get_repository() -> BaseTaskRepository:
    """Factory function to get singleton repository based on config."""
    if settings.REPOSITORY_TYPE.lower() == "in_memory":
        return InMemoryTaskRepository()
    else:
        return SQLiteTaskRepository(db_path=settings.SQLITE_DB_PATH)


def get_task_manager(repo: BaseTaskRepository = Depends(get_repository)) -> TaskManager:
    """Dependency provider for TaskManager service."""
    return TaskManager(repository=repo)
