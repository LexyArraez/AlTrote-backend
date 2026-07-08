from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str
    app_version: str
    app_description: str
    database_url: str

    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 horas

    # Almacenamiento de imagenes
    upload_dir: str = "uploads"
    max_upload_size_mb: int = 5

    class Config:  # donde tiene que ir a buscar las variables de entorno
        env_file = '.env'

settings = Settings()