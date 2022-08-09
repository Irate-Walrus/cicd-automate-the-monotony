from pydantic import BaseSettings

class Settings(BaseSettings):
    # Base
    debug: bool = False
    project_name: str = "cicd-automate-the-monotony-todo-api"
    description: str = "Example application for presentation \"CI/CD - Automated The Monotony\" for Monash University"

    # Database
    db_async_connection_str: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
