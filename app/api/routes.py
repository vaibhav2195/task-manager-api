from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.api.dependencies import get_task_manager
from app.exceptions import TaskAppException, TaskNotFoundError, TaskValidationError
from app.metrics import TASK_COUNT_GAUGE
from app.models.task import TaskCreate, TaskResponse, TaskUpdate
from app.services.task_manager import TaskManager

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate,
    manager: TaskManager = Depends(get_task_manager),
):
    """Create a new task."""
    try:
        task = manager.create_task(
            title=payload.title,
            description=payload.description,
            priority=payload.priority,
        )
        TASK_COUNT_GAUGE.set(manager.get_task_count())
        return task.to_dict()
    except TaskValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except TaskAppException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message)


@router.get("", response_model=List[TaskResponse])
def list_tasks(
    completed: Optional[bool] = Query(default=None, description="Filter by completion status"),
    limit: int = Query(default=100, ge=1, le=500, description="Max items to return"),
    offset: int = Query(default=0, ge=0, description="Offset index"),
    manager: TaskManager = Depends(get_task_manager),
):
    """List tasks with optional completion filter and pagination."""
    tasks = manager.list_tasks(completed=completed, limit=limit, offset=offset)
    TASK_COUNT_GAUGE.set(manager.get_task_count())
    return [t.to_dict() for t in tasks]


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: str,
    manager: TaskManager = Depends(get_task_manager),
):
    """Get a specific task by ID."""
    try:
        task = manager.get_task_by_id(task_id)
        return task.to_dict()
    except TaskNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: str,
    payload: TaskUpdate,
    manager: TaskManager = Depends(get_task_manager),
):
    """Update an existing task."""
    try:
        task = manager.update_task(
            task_id=task_id,
            title=payload.title,
            description=payload.description,
            completed=payload.completed,
            priority=payload.priority,
        )
        return task.to_dict()
    except TaskNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except TaskValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: str,
    manager: TaskManager = Depends(get_task_manager),
):
    """Delete a task by ID."""
    try:
        manager.delete_task(task_id)
        TASK_COUNT_GAUGE.set(manager.get_task_count())
        return None
    except TaskNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
