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
import i18n

# Third party libs ------------------------------------------------------------

import discord
from discord.ext import commands

# Project modules -------------------------------------------------------------

import allay

# I18N config -----------------------------------------------------------------

i18n.translations.container.clear()  # invalidate old cache
i18n.set("filename_format", "{locale}.{format}")
i18n.set("fallback", "en")

# Get all lang paths
i18n.load_path.append("allay/core/langs")
for plugin in allay.builtins.all:
    plugin_path = os.path.join(allay.builtins.path, plugin, "langs")
    if os.path.isdir(plugin_path):
        i18n.load_path.append(plugin_path)
for plugin in allay.plugins.all:
    plugin_path = os.path.join(allay.plugins.path, plugin, "langs")
    if os.path.isdir(plugin_path):
        i18n.load_path.append(plugin_path)

#==============================================================================
# Plugin
#==============================================================================

class Languages(commands.Cog):
    
    def __init__(self, bot:allay.Bot):
        self.bot = bot
        self.file = "languages"
        self.languages = ["fr", "en"]
        self.config_options = ["language"]

    async def tr(self, ctx, key: str, **kwargs): # pylint: disable=invalid-name
        """Translate something
        Ctx can be either a Context, a guild, a guild id, a channel or a lang directly"""
        lang = self.languages[0]
        if isinstance(ctx, commands.Context):
            if ctx.guild:
                lang = await self.get_lang(ctx.guild.id, use_str=True)
        elif isinstance(ctx, discord.Guild):
            lang = await self.get_lang(ctx.id, use_str=True)
        elif isinstance(ctx, discord.abc.GuildChannel):
            lang = await self.get_lang(ctx.guild.id, use_str=True)
        elif isinstance(ctx, str) and ctx in self.languages:
            lang = ctx
        elif isinstance(ctx, int):  # guild ID
            if self.bot.get_guild(ctx):  # if valid guild
                lang = await self.get_lang(ctx, use_str=True)
            else:
                lang = self.languages[0]
        return i18n.t(key, locale=lang, **kwargs)

    async def get_lang(self, guild_id: int, use_str: bool = False) -> int:
        if guild_id is None:
            as_int = 0
        else:
            # migration for old format
            if isinstance(self.bot.server_configs[guild_id]["language"], int):
                as_int = self.bot.server_configs[guild_id]["language"]
            else:
                as_int = self.languages.index(
                    self.bot.server_configs[guild_id]["language"]
                )
        if use_str:
            return self.languages[as_int]
        return as_int


