from datetime import datetime, timezone
from typing import Optional
import uuid
from pydantic import BaseModel, Field
from app.exceptions import TaskValidationError


class TaskPriority:
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

    @classmethod
    def valid_priorities(cls):
        return {cls.LOW, cls.MEDIUM, cls.HIGH}


class Task:
    """Domain Model representing a Task using OOP principles."""

    def __init__(
        self,
        title: str,
        description: Optional[str] = "",
        completed: bool = False,
        priority: str = TaskPriority.MEDIUM,
        task_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self._id = task_id or str(uuid.uuid4())
        self.set_title(title)
        self.set_description(description)
        self.completed = completed
        self.set_priority(priority)
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)

    @property
    def id(self) -> str:
        return self._id

    @property
    def title(self) -> str:
        return self._title

    def set_title(self, title: str) -> None:
        if not title or not title.strip():
            raise TaskValidationError("Task title cannot be empty.")
        if len(title.strip()) > 200:
            raise TaskValidationError("Task title cannot exceed 200 characters.")
        self._title = title.strip()

    @property
    def description(self) -> str:
        return self._description

    def set_description(self, description: Optional[str]) -> None:
        desc = description or ""
        if len(desc) > 1000:
            raise TaskValidationError("Task description cannot exceed 1000 characters.")
        self._description = desc.strip()

    @property
    def priority(self) -> str:
        return self._priority

    def set_priority(self, priority: str) -> None:
        p_lower = priority.lower() if priority else TaskPriority.MEDIUM
        if p_lower not in TaskPriority.valid_priorities():
            raise TaskValidationError(
                f"Invalid priority '{priority}'. Must be one of {TaskPriority.valid_priorities()}."
            )
        self._priority = p_lower

    def mark_completed(self) -> None:
        self.completed = True
        self.touch()

    def mark_incomplete(self) -> None:
        self.completed = False
        self.touch()

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)

    def update(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        completed: Optional[bool] = None,
        priority: Optional[str] = None,
    ) -> None:
        if title is not None:
            self.set_title(title)
        if description is not None:
            self.set_description(description)
        if completed is not None:
            self.completed = completed
        if priority is not None:
            self.set_priority(priority)
        self.touch()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        created_at = (
            datetime.fromisoformat(data["created_at"])
            if isinstance(data.get("created_at"), str)
            else data.get("created_at")
        )
        updated_at = (
            datetime.fromisoformat(data["updated_at"])
            if isinstance(data.get("updated_at"), str)
            else data.get("updated_at")
        )
        return cls(
            task_id=data.get("id"),
            title=data.get("title", ""),
            description=data.get("description", ""),
            completed=data.get("completed", False),
            priority=data.get("priority", TaskPriority.MEDIUM),
            created_at=created_at,
            updated_at=updated_at,
        )

    def __repr__(self) -> str:
        return f"<Task id={self.id} title='{self.title}' completed={self.completed}>"


# Pydantic DTO Schemas for API Serialization


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, example="Buy groceries")
    description: Optional[str] = Field(default="", max_length=1000, example="Milk, Bread, Eggs")
    priority: Optional[str] = Field(default="medium", example="high")


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: Optional[bool] = Field(default=None)
    priority: Optional[str] = Field(default=None)


class TaskResponse(BaseModel):
    id: str
    title: str
    description: str
    completed: bool
    priority: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
