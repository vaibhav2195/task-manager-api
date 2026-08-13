class TaskAppException(Exception):
    """Base exception class for Task Manager application."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class TaskNotFoundError(TaskAppException):
    """Raised when a requested task is not found."""

    def __init__(self, task_id: str):
        self.task_id = task_id
        super().__init__(f"Task with ID '{task_id}' was not found.")


class TaskValidationError(TaskAppException):
    """Raised when task data fails validation rules."""

    def __init__(self, message: str):
        super().__init__(message)


class RepositoryError(TaskAppException):
    """Raised when database or storage operations fail."""

    def __init__(self, message: str):
        super().__init__(f"Repository error: {message}")


class DuplicateTaskError(TaskAppException):
    """Raised when attempting to create a task that already exists."""

    def __init__(self, task_id: str):
        self.task_id = task_id
        super().__init__(f"Task with ID '{task_id}' already exists.")
