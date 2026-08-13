import pytest
from app.exceptions import DuplicateTaskError, TaskNotFoundError
from app.models.task import Task


@pytest.mark.parametrize("repo_fixture", ["in_memory_repo", "sqlite_repo"])
def test_repository_crud(request, repo_fixture):
    repo = request.getfixturevalue(repo_fixture)

    # 1. Create
    task = Task(title="Repo Task", description="Testing repository", priority="high")
    created = repo.create(task)
    assert created.id == task.id
    assert repo.count() == 1

    # 2. Get by ID
    retrieved = repo.get_by_id(task.id)
    assert retrieved is not None
    assert retrieved.title == "Repo Task"
    assert retrieved.priority == "high"

    # 3. Get All & Filtering
    all_tasks = repo.get_all()
    assert len(all_tasks) == 1

    # 4. Update
    task.update(title="Updated Repo Task", completed=True)
    updated = repo.update(task)
    assert updated.title == "Updated Repo Task"
    assert updated.completed is True

    # Check filtering by completed status
    completed_tasks = repo.get_all(completed=True)
    assert len(completed_tasks) == 1
    incomplete_tasks = repo.get_all(completed=False)
    assert len(incomplete_tasks) == 0

    # 5. Delete
    deleted = repo.delete(task.id)
    assert deleted is True
    assert repo.get_by_id(task.id) is None
    assert repo.count() == 0

    # Delete non-existent
    assert repo.delete("non-existent-id") is False


@pytest.mark.parametrize("repo_fixture", ["in_memory_repo", "sqlite_repo"])
def test_repository_duplicate_create(request, repo_fixture):
    repo = request.getfixturevalue(repo_fixture)
    task = Task(title="Duplicate Test")
    repo.create(task)

    with pytest.raises(DuplicateTaskError):
        repo.create(task)


@pytest.mark.parametrize("repo_fixture", ["in_memory_repo", "sqlite_repo"])
def test_repository_update_not_found(request, repo_fixture):
    repo = request.getfixturevalue(repo_fixture)
    task = Task(title="Ghost Task")

    with pytest.raises(TaskNotFoundError):
        repo.update(task)
