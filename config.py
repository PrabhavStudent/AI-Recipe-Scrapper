from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./recipe_ai.db"
    db_user: str = "root"
    db_password: str = "root"
    db_host: str = "localhost"
    db_port: int = 3306
    db_name: str = "recipe_ai"
    gemini_api_key: str = ""
    llm_model: str = "gemini-1.5-flash"
    frontend_origin: str = "http://127.0.0.1:5173"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def sqlalchemy_database_url(self) -> str:
        if self.database_url:
            return self.database_url

        password = quote_plus(self.db_password)
        return f"mysql+pymysql://{self.db_user}:{password}@{self.db_host}:{self.db_port}/{self.db_name}"


settings = Settings()
