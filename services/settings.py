from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


ENV_FILE = Path(__file__).resolve().parent.parent / ".env"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore") 
     # This configuration tells Pydantic to load environment variables from the .env file,
     # use UTF-8 encoding, and ignore any extra fields that are not defined in the Settings class. 
     # This allows you to easily manage your application's configuration settings and keep sensitive information secure.

    # For postgresql connection string 
    DB_CONNECTION: str # The connection string for the database, which is required for the application to function properly.
    
    # for mysql connection string
    # DB_CONNECTION: str = Field(validation_alias="DATABASE_URL")     # validation_alias means which external name should be used when loading or validating data

    SECRET_KEY: str
    ALGORITHM: str
    EXPIRE_MINUTES: int
    
    # Mail (optional) - used by services/send_email.py
    MAIL_USERNAME: Optional[str] = None
    MAIL_PASSWORD: Optional[str] = None
    MAIL_FROM: Optional[str] = None
    MAIL_SERVER: Optional[str] = None
    MAIL_PORT: int = 587
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False

settings = Settings()