from pydantic_settings import BaseSettings, SettingsConfigDict


# class Settings(BaseSettings):
#     sqlalchemy_database_url: str
#     secret_key: str
#     algorithm: str
#     mail_username: str
#     mail_password: str
#     mail_from: str
#     mail_port: int
#     mail_server: str
#     redis_host: str = 'localhost'
#     redis_port: int = 6379

#     class Config:
#         env_file = ".env"
#         env_file_encoding = "utf-8"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='allow'
    )

settings = Settings()