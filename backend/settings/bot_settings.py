from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore"
    )
    token: str = Field(default="")
    admin_ids: list[int] = Field(default=[])
    use_redis: str = Field(default=True)
    channel_id: int | None = Field(default=None)
