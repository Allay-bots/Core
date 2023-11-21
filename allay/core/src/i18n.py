"""
Ce programme est régi par la licence CeCILL soumise au droit français et
respectant les principes de diffusion des logiciels libres. Vous pouvez
utiliser, modifier et/ou redistribuer ce programme sous les conditions
de la licence CeCILL diffusée sur le site "http://www.cecill.info".
"""

#==============================================================================
# Requirements
#==============================================================================

import os

import discord
import i18n
from discord.ext import commands

import allay

# I18N config -----------------------------------------------------------------

i18n.translations.container.clear()  # invalidate old cache
i18n.set("filename_format", "{locale}.{format}")
i18n.set("fallback", "en")

# Get all lang paths
i18n.load_path.append("allay/core/langs")
for plugin in allay.builtins.all_modules:
    plugin_path = os.path.join(allay.builtins.path, plugin, "langs")
    if os.path.isdir(plugin_path):
        i18n.load_path.append(plugin_path)
for plugin in allay.plugins.all_modules:
    plugin_path = os.path.join(allay.plugins.path, plugin, "langs")
    if os.path.isdir(plugin_path):
        i18n.load_path.append(plugin_path)

#==============================================================================
# I18N class
#==============================================================================

class I18N:
    "Handle generic internationalization of our bot"

    CTX_TYPE = discord.abc.User | discord.Guild | discord.abc.GuildChannel | discord.Locale | \
        commands.Context | discord.Interaction | int

    @staticmethod
    def tr(ctx: CTX_TYPE, key: str, **kwargs): # pylint: disable=invalid-name
        "Translate a key to the context language"
        return i18n.t(key, locale=str(I18N.get_locale(ctx)), **kwargs)

    @staticmethod
    def get_locale(ctx: CTX_TYPE) -> discord.Locale:
        "Get the locale that should be used for a given context"
        if isinstance(ctx, discord.Locale):
            return ctx
        if isinstance(ctx, discord.Guild):
            return ctx.preferred_locale
        try:
            return ctx.locale # type: ignore
        except AttributeError:
            pass
        try:
            return ctx.guild.preferred_locale # type: ignore
        except AttributeError:
            pass
        return discord.Locale.american_english
