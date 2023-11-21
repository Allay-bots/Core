"""
Ce programme est régi par la licence CeCILL soumise au droit français et
respectant les principes de diffusion des logiciels libres. Vous pouvez
utiliser, modifier et/ou redistribuer ce programme sous les conditions
de la licence CeCILL diffusée sur le site "http://www.cecill.info".
"""

#==============================================================================
# Requirements
#==============================================================================

# Standard libs ---------------------------------------------------------------

import os
from json import dump, load
from typing import Any, Literal, Optional, TypedDict

# Third party libs ------------------------------------------------------------

from discord.ext import commands

# Project modules -------------------------------------------------------------

import allay


#==============================================================================
# Typing
#==============================================================================

class ConfigOption(TypedDict):
    "Represents a configuration option definition"
    default: Any
    type: Literal[
        "roles", "channels", "categories", "text", "emojis", "modlogsFlags", "int"
    ]
    command: Optional[str]

ServerConfigDict = dict[str, int | str | list[int] | list[str] | bool]

#==============================================================================
# Global data
#==============================================================================

CONFIG_OPTIONS: dict[str, ConfigOption] = {}

CONFIG_OPTIONS.update(
    {
        "language": {
            "default": allay.BotConfig.get("core.default_language"),
            "type": "text",
            "command": 'language',
        },
        "admins": {
            "default": allay.BotConfig.get("core.admins"),
            "type": "categories",
            "command": None,
        },
    }
)

CONFIG_FOLDER = "configs"

CONFIG_TEMPLATE = {
    k: v["default"]
    for k, v in CONFIG_OPTIONS.items()
    if "default" in v
}

#==============================================================================
# Plugin
#==============================================================================

class ServerConfig(ServerConfigDict):
    "Represents the configuration of a bot guild"

    def __init__(self, manager: "ConfigManager", server_id: int, config: ServerConfigDict):
        super().__init__(config)
        self.manager = manager
        self.guild_id = server_id

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError as exc:
            if key in CONFIG_TEMPLATE.keys():
                return CONFIG_TEMPLATE[key]
            raise exc

    def __setitem__(self, key, item):
        if key in CONFIG_TEMPLATE.keys():
            super().__setitem__(key, item)
            self.manager[self.guild_id] = self
        else:
            raise ValueError("Invalid config key")

    def __delitem__(self, key):
        super().__setitem__(key, CONFIG_TEMPLATE[key])
        self.manager[self.guild_id] = self


class ConfigManager(dict[int, ServerConfigDict]):
    """Handle the whole bot configuration for every guild
    
    Guild configurations are stored in separated .json files"""

    def __init__(self):
        super().__init__()
        self.cache: dict[int, ServerConfigDict] = {}

    def __setitem__(self, key: int | str, config: ServerConfigDict):
        if not (isinstance(key, int) or key.isnumeric()):
            raise ValueError("Key need to be a valid guild ID")
        guild_id = int(key)
        allowed_keys = CONFIG_TEMPLATE.keys()
        config = { k: v for k, v in config.items() if k in allowed_keys }
        with open(f"{CONFIG_FOLDER}/{guild_id}.json", "w", encoding="utf8") as f:
            dump(config, f)
        self.cache[int(guild_id)] = config

    def __getitem__(self, key: int | str):
        if not (isinstance(key, int) or key.isnumeric()):
            raise ValueError("Key need to be a valid guild ID")
        guild_id = int(key)
        result = dict(CONFIG_TEMPLATE)
        if guild_id not in self.cache:
            try:
                with open(f"{CONFIG_FOLDER}/{guild_id}.json", "r", encoding="utf8") as f:
                    self.cache[guild_id] = load(f)
            except FileNotFoundError:
                self.cache[guild_id] = result
        result.update(self.cache[guild_id])
        allowed_keys = CONFIG_TEMPLATE.keys()
        result = { k: v for k, v in result.items() if k in allowed_keys }
        return ServerConfig(self, guild_id, result)

    def __repr__(self):
        return "<ConfigManager>"

    def __len__(self):
        return len(
            [name for name in os.listdir(CONFIG_FOLDER) if os.path.isfile(name)]
        )

    def __delitem__(self, key: int | str):
        if not (isinstance(key, int) or key.isnumeric()):
            raise ValueError("Key need to be a valid guild ID")
        guild_id = int(key)
        os.remove(f"{CONFIG_FOLDER}/{guild_id}.json")
        if guild_id in self.cache:
            del self.cache[guild_id]

    def has_key(self, k):
        "Check if a guild has a configuration file"
        return os.path.isfile(f"{CONFIG_FOLDER}/{k}.json")

    def update(self, *args: dict[int, ServerConfigDict], **kwargs: ServerConfigDict):
        for arg in args:
            if isinstance(arg, dict):
                for key, value in arg.items():
                    self[key] = value
        for guild_id, guild_config in kwargs.items():
            self[guild_id] = guild_config

    def keys(self):
        return [int(name) for name in os.listdir(CONFIG_FOLDER) if os.path.isfile(name)]

    def __contains__(self, item: int):
        return item in self

class ConfigCog(commands.Cog):
    "Bot cog to handle guild configuration"
    def __init__(self, bot):
        self.bot = bot
        self.file = "configManager"
        self.conf_manager = ConfigManager()
