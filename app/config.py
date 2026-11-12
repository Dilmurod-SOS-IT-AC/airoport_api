from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL

class Settings(BaseSettings):
    db_user: str = "postgres"
    db_password: str = "12345"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "airoport_db"

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername="postgresql+pg8000",
            username=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
        )

settings = Settings()