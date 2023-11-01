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

class I18N:

    @staticmethod
    async def tr(ctx, key: str, **kwargs): # pylint: disable=invalid-name
        """Translate something
        Ctx can be either a Context, a guild, a guild id, a channel or a lang directly"""
        locale = await I18N.get_locale(ctx)
        return i18n.t(key, locale=str(locale), **kwargs)

    @staticmethod
    async def get_locale(ctx):
        if isinstance(ctx, discord.Locale):
            return ctx
        
        # TODO: Consider the user locale
        # if isinstance(ctx, discord.abc.User):
        #     user = ctx
        #     if isinstance(ctx, discord.Member):
        #         for bot in allay.Bot.instances:
        #             if (u := bot.get_user(ctx.id)) is not None:
        #                 user = u
        #     return user.locale

        if (locale := ctx.guild.preferred_locale) is not None:
            return locale
        return discord.Locale.american_english



