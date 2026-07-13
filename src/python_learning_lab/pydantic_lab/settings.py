"""使用 pydantic-settings 校验环境变量。"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LAB_", env_file=".env", extra="ignore")

    app_name: str = "Python Learning Lab"
    debug: bool = False
    host: str = "127.0.0.1"
    port: int = Field(default=8000, ge=1, le=65535)

