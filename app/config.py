import os
from pydantic import BaseModel


class Settings(BaseModel):
    PROJECT_NAME: str = "Task Manager REST API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = ""
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Repository backend type: 'in_memory' or 'sqlite'
    REPOSITORY_TYPE: str = os.getenv("REPOSITORY_TYPE", "sqlite")

    # SQLite Configuration
    SQLITE_DB_PATH: str = os.getenv("SQLITE_DB_PATH", "tasks.db")


settings = Settings()
