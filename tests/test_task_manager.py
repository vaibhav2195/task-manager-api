import pytest
from app.exceptions import TaskNotFoundError
from app.services.task_manager import TaskManager


def test_task_manager_create_and_get(task_manager: TaskManager):
    task = task_manager.create_task(
        title="Manager Task", description="Via TaskManager", priority="low"
    )
    assert task.id is not None
    assert task.title == "Manager Task"
    assert task_manager.get_task_count() == 1

    fetched = task_manager.get_task_by_id(task.id)
    assert fetched.id == task.id
    assert fetched.description == "Via TaskManager"


def test_task_manager_get_not_found(task_manager: TaskManager):
    with pytest.raises(TaskNotFoundError):
        task_manager.get_task_by_id("non-existent-id")


def test_task_manager_list_tasks(task_manager: TaskManager):
    task_manager.create_task(title="Task 1", priority="low")
    task_manager.create_task(title="Task 2", priority="high")

    tasks = task_manager.list_tasks()
    assert len(tasks) == 2


def test_task_manager_update(task_manager: TaskManager):
    task = task_manager.create_task(title="Initial Title")
    updated = task_manager.update_task(task.id, title="Updated Title", completed=True)

    assert updated.title == "Updated Title"
    assert updated.completed is True


def test_task_manager_delete(task_manager: TaskManager):
    task = task_manager.create_task(title="To Be Deleted")
    assert task_manager.get_task_count() == 1

    task_manager.delete_task(task.id)
    assert task_manager.get_task_count() == 0

    with pytest.raises(TaskNotFoundError):
        task_manager.delete_task(task.id)
