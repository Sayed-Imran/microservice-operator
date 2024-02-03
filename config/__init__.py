from typing import Literal
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
load_dotenv()

class _EnvConfig(BaseSettings):
    """Base configuration."""
    ENV: Literal["dev", "test", "prod"] = "dev"

EnvConfig = _EnvConfig()
