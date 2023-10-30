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

# Third party libs ------------------------------------------------------------

import discord
from discord.ext import commands

# Project modules -------------------------------------------------------------

from allay.core.src.bot_config import BotConfig
from allay.core.src.discord import Context

#==============================================================================
# Checks
#==============================================================================

# Custom exceptions -----------------------------------------------------------

class CheckException(commands.CommandError):
    """
    Exception personnalisée pour les checks
    """
    def __init__(self, check_id, *args):
        super().__init__(message=f"Custom check '{check_id}' failed", *args)
        self.id = check_id # pylint: disable=invalid-name

# Is bot admin ----------------------------------------------------------------

def is_bot_admin(ctx: Context):
    return ctx.author.id in BotConfig.get("bot.admins")


async def is_admin(ctx: Context):
    admin = (
        ctx.guild is None
        or ctx.author.guild_permissions.administrator
        or is_bot_admin(ctx)
    )
    if not admin:
        raise CheckException("is_admin")
    return True

# Is server manager -----------------------------------------------------------

async def is_server_manager(ctx: Context):
    g_manager = (
        ctx.guild is None
        or ctx.author.guild_permissions.manage_guild
        or is_bot_admin(ctx)
    )
    if not g_manager:
        raise CheckException("is_server_manager")
    return True

# Is roles manager ------------------------------------------------------------

async def is_roles_manager(ctx: Context):
    r_manager = (
        ctx.guild is None
        or ctx.author.guild_permissions.manage_roles
        or is_bot_admin(ctx)
    )
    if not r_manager:
        raise CheckException("is_roles_manager")
    return True

# Can group -------------------------------------------------------------------

async def can_group(ctx: Context):
    server_config = ctx.bot.server_configs[ctx.guild.id]
    if server_config["group_allowed_role"] is None:
        return True
    role = discord.utils.get(ctx.message.guild.roles, id=server_config["group_allowed_role"])
    if role in ctx.author.roles:
        return True
