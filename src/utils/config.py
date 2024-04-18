from dataclasses import dataclass
from dotenv import dotenv_values


@dataclass
class Config:
    bot_name: str
    bot_prefix: str
    bot_token: str
    bot_invite: str
    bot_owner: int
    bot_join_message: str
    bot_status_type: str
    bot_activity_type: str
    bot_activity_name: str
    support_guild_server: int
    support_guild_invite: str
    support_guild_join: int
    support_guild_leave: int
    support_guild_bot_errors: int
    support_guild_category: str

    @classmethod
    def from_dict(self, **kwargs) -> "Config":
        kwargs_overwrite = {}

        for key, value in kwargs.items():
            new_key = key.lower()

            if value.isdigit():
                kwargs_overwrite[new_key] = int(value)
            else:
                kwargs_overwrite[new_key] = value

        return Config(**kwargs_overwrite)

    @classmethod
    def from_env(self, filename: str = ".env") -> "Config":
        return Config.from_dict(**dotenv_values(filename))
    