from functools import lru_cache

from pydantic import Field
from pydantic_settings import SettingsConfigDict, BaseSettings

from settings.bot_settings import BotSettings
from settings.db_settings import DatabaseSettings, RedisSettings
from settings.logging_settings import LoggingSettings
from settings.miscellaneous_settings import MiscellaneousSettings


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str('.env.prod'),
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    app_version: str = Field(default="1.0.0")
    is_development: bool = Field(default=False)

    postgres: DatabaseSettings
    logging: LoggingSettings
    bot: BotSettings
    redis: RedisSettings
    misc: MiscellaneousSettings = Field(default_factory=MiscellaneousSettings)


@lru_cache(maxsize=1)
def get_app_settings() -> AppSettings:
    return AppSettings()
