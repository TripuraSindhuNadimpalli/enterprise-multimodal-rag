from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Enterprise Multimodal RAG"
    app_version: str = "0.1.0"
    environment: str = "development"

    postgres_host: str = "localhost"
    postgres_port: int = 55433
    postgres_db: str = "enterprise_rag"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"


    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "enterprise-documents"
    minio_secure: bool = False

    redis_host: str = "localhost"
    redis_port: int = 6380

    jwt_secret_key: str = "change-this-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_minutes: int = 60

    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()