"""
Ce programme est régi par la licence CeCILL soumise au droit français et
respectant les principes de diffusion des logiciels libres. Vous pouvez
utiliser, modifier et/ou redistribuer ce programme sous les conditions
de la licence CeCILL diffusée sur le site "http://www.cecill.info".
"""

__version__ = "0.0.1"

from allay.core.src import bot_config, database, discord, i18n

# Shortcuts -------------------------------------------------------------------

from allay.core.src.discord import Bot
from allay.core.src.bot_config import BotConfig
from allay.core.src.discord import checks
from allay.core.src.discord import Context
from allay.core.src.database import Database
from allay.core.src.discord import GuildConfig
from allay.core.src.i18n import I18N

__all__ = [
    "bot_config",
    "database",
    "discord",
    "i18n",

    "Bot",
    "BotConfig",
    "checks",
    "Context",
    "Database",
    "GuildConfig",
    "I18N",
]
