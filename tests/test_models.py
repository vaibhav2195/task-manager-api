from datetime import datetime
import pytest
from app.exceptions import TaskValidationError
from app.models.task import Task


def test_task_creation():
    task = Task(title="Study CI/CD", description="Learn Docker and GitHub Actions", priority="high")
    assert task.title == "Study CI/CD"
    assert task.description == "Learn Docker and GitHub Actions"
    assert task.priority == "high"
    assert task.completed is False
    assert task.id is not None
    assert isinstance(task.created_at, datetime)
    assert isinstance(task.updated_at, datetime)


def test_task_title_validation_empty():
    with pytest.raises(TaskValidationError) as exc:
        Task(title="")
    assert "Task title cannot be empty" in str(exc.value)


def test_task_title_validation_too_long():
    with pytest.raises(TaskValidationError) as exc:
        Task(title="a" * 201)
    assert "Task title cannot exceed 200 characters" in str(exc.value)


def test_task_description_validation_too_long():
    with pytest.raises(TaskValidationError) as exc:
        Task(title="Valid Title", description="a" * 1001)
    assert "Task description cannot exceed 1000 characters" in str(exc.value)


def test_task_priority_validation():
    with pytest.raises(TaskValidationError) as exc:
        Task(title="Valid Title", priority="super_urgent")
    assert "Invalid priority 'super_urgent'" in str(exc.value)


def test_task_mark_completed_and_incomplete():
    task = Task(title="Test Task")
    assert task.completed is False

    old_updated_at = task.updated_at
    task.mark_completed()
    assert task.completed is True
    assert task.updated_at >= old_updated_at

    task.mark_incomplete()
    assert task.completed is False


def test_task_update_method():
    task = Task(title="Old Title", description="Old Desc", priority="low")
    task.update(title="New Title", description="New Desc", completed=True, priority="high")

    assert task.title == "New Title"
    assert task.description == "New Desc"
    assert task.completed is True
    assert task.priority == "high"


def test_task_to_dict_and_from_dict():
    task = Task(title="Serialization Test", description="Test json dict", priority="medium")
    data = task.to_dict()

    assert data["id"] == task.id
    assert data["title"] == "Serialization Test"
    assert data["description"] == "Test json dict"
    assert data["priority"] == "medium"
    assert data["completed"] is False

    reconstructed = Task.from_dict(data)
    assert reconstructed.id == task.id
    assert reconstructed.title == task.title
    assert reconstructed.description == task.description
    assert reconstructed.priority == task.priority
    assert reconstructed.completed == task.completed
