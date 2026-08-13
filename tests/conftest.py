import os
import tempfile
import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_repository
from app.main import app
from app.models.task import Task
from app.repositories.in_memory import InMemoryTaskRepository
from app.repositories.sqlite import SQLiteTaskRepository
from app.services.task_manager import TaskManager


@pytest.fixture
def sample_task_data():
    return {
        "title": "Test Task",
        "description": "This is a test task description",
        "priority": "high",
    }


@pytest.fixture
def sample_task(sample_task_data):
    return Task(
        title=sample_task_data["title"],
        description=sample_task_data["description"],
        priority=sample_task_data["priority"],
    )


@pytest.fixture
def in_memory_repo():
    repo = InMemoryTaskRepository()
    yield repo
    repo.clear()


@pytest.fixture
def sqlite_repo():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        tmp_db_path = tmp.name

    repo = SQLiteTaskRepository(db_path=tmp_db_path)
    yield repo
    repo.clear()
    if os.path.exists(tmp_db_path):
        os.remove(tmp_db_path)


@pytest.fixture
def task_manager(in_memory_repo):
    return TaskManager(repository=in_memory_repo)


@pytest.fixture
def client():
    # Fresh repository for each API test
    test_repo = InMemoryTaskRepository()
    app.dependency_overrides[get_repository] = lambda: test_repo
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
