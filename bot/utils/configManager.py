"""
Ce programme est régi par la licence CeCILL soumise au droit français et
respectant les principes de diffusion des logiciels libres. Vous pouvez
utiliser, modifier et/ou redistribuer ce programme sous les conditions
de la licence CeCILL diffusée sur le site "http://www.cecill.info".
"""

import os
from json import dump, load

from discord.ext import commands

from utils import Gunibot, CONFIG_OPTIONS

CONFIG_FOLDER = "configs"

CONFIG_TEMPLATE = {k: v["default"] for k, v in CONFIG_OPTIONS.items() if "default" in v}


class ServerConfig(dict):
    def __init__(self, manager, serverID, value):
        super().__init__(value)
        self.manager = manager
        self.server_id = serverID

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
            self.manager[self.server_id] = self
        else:
            raise ValueError("Invalid config key")

    def __delitem__(self, key):
        super().__setitem__(key, CONFIG_TEMPLATE[key])
        self.manager[self.server_id] = self


class ConfigCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file = "configManager"
        self.conf_manager = self.ConfigManager()

    class ConfigManager(dict):
        def __init__(self):
            super().__init__()
            self.cache = dict()

        def __setitem__(self, key, item):
            if not (isinstance(key, int) or key.isnumeric()):
                raise ValueError("Key need to be a valid guild ID")
            allowed_keys = CONFIG_TEMPLATE.keys()
            item = {k: v for k, v in item.items() if k in allowed_keys}
            with open(f"{CONFIG_FOLDER}/{key}.json", "w", encoding="utf8") as f:
                dump(item, f)
            self.cache[key] = item

        def __getitem__(self, key):
            if not (isinstance(key, int) or key.isnumeric()):
                raise ValueError("Key need to be a valid guild ID")
            result = dict(CONFIG_TEMPLATE)
            if key not in self.cache:
                try:
                    with open(f"{CONFIG_FOLDER}/{key}.json", "r", encoding="utf8") as f:
                        self.cache[key] = load(f)
                except FileNotFoundError:
                    self.cache[key] = result
            result.update(self.cache[key])
            allowed_keys = CONFIG_TEMPLATE.keys()
            result = {k: v for k, v in result.items() if k in allowed_keys}
            return ServerConfig(self, key, result)

        def __repr__(self):
            return "<configManager>"

        def __len__(self):
            return len(
                [name for name in os.listdir(CONFIG_FOLDER) if os.path.isfile(name)]
            )

        def __delitem__(self, key):
            pass

        def has_key(self, k):
            return os.path.isfile(f"{CONFIG_FOLDER}/{k}.json")

        def update(self, *args, **kwargs):
            for arg in args:
                if isinstance(arg, dict):
                    for key, value in arg.items():
                        self[key] = value
            for kwarg in kwargs:
                for key, value in kwarg.items():
                    self[key] = value

        def keys(self):
            return [name for name in os.listdir(CONFIG_FOLDER) if os.path.isfile(name)]

        # def values(self):
        #     return self.__dict__.values()

        # def items(self):
        #     return self.__dict__.items()

        # def pop(self, *args):
        #     return self.__dict__.pop(*args)

        def __contains__(self, item):
            return item in self

    class LogsFlags:
        FLAGS = {
            1 << 0: "messages",
            1 << 1: "joins",
            1 << 2: "invites",
            1 << 3: "voice",
            1 << 4: "moderation",
            1 << 5: "boosts",
            1 << 6: "roles",
            1 << 7: "members",
            1 << 8: "emojis",
        }

        def flags_to_int(self, flags: list) -> int:
            r = 0
            for k, v in self.FLAGS.items():
                if v in flags:
                    r |= k
            return r

        def int_to_flags(self, i: int) -> list:
            return [v for k, v in self.FLAGS.items() if i & k == k]


async def setup(bot: Gunibot = None):
    await bot.add_cog(ConfigCog(bot))
