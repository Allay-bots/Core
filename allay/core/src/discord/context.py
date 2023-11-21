from typing import TYPE_CHECKING

import discord
from discord.ext import commands

if TYPE_CHECKING:
    from allay.core.src.discord import Bot


class Context(commands.Context):
    """Replacement for the official commands.Context class
    It allows us to add more methods and properties in the whole bot code"""
    bot: "Bot"

    @property
    def bot_permissions(self) -> discord.Permissions:
        """Permissions of the bot in the current context"""
        if self.guild:
            # message in a guild
            return self.channel.permissions_for(self.guild.me)
        # message in DM
        return self.channel.permissions_for(self.bot) # type: ignore

    @property
    def user_permissions(self) -> discord.Permissions:
        """Permissions of the message author in the current context"""
        return self.channel.permissions_for(self.author) # type: ignore

    @property
    def can_send_embed(self) -> bool:
        """If the bot has the right permissions to send an embed in the current context"""
        return self.bot_permissions.embed_links
