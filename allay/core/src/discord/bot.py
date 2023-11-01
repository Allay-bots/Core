
#==============================================================================
# Import requirements
#==============================================================================

# Standard libs ---------------------------------------------------------------

import os
import sqlite3
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Dict, List, Optional, Union

# Thrid party libs ------------------------------------------------------------

import discord
from discord.ext import commands
from LRFutils import logs

# Project modules -------------------------------------------------------------

from allay.core.src.discord.context import Context
from allay.core.src.bot_config import BotConfig

#==============================================================================
# Bot class
#==============================================================================

class Bot(commands.bot.AutoShardedBot):

    instances = []

    def __init__(self, case_insensitive=None, status=None, database=None):
        
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix=self.get_prefix,
            case_insensitive=case_insensitive,
            status=status,
            allowed_mentions=discord.AllowedMentions(everyone=False, roles=False),
            intents=intents,
        )
        
        self.database = database
        self.database.row_factory = sqlite3.Row
        self.cog_icons = {}
        self.cog_display_names = {}
        self.app_commands_list: Optional[list[discord.app_commands.AppCommand]] = None

        Bot.instances.append(self)

    # Context -----------------------------------------------------------------

    # pylint: disable=arguments-differ
    async def get_context(self, message: discord.Message, *, cls=Context):
        """
        Récupérer le contexte d'une commande

        :param message: Le message
        :param cls: La classe du contexte
        :return: Le contexte
        """
        # when you override this method, you pass your new Context
        # subclass to the super() method, which tells the bot to
        # use the new MyContext class
        return await super().get_context(message, cls=cls)

    # Server config -----------------------------------------------------------

    @property
    def server_configs(self):
        """
        Récupérer la configuration du serveur

        :return: La configuration du serveur
        """
        return self.get_cog("ConfigCog").conf_manager

    @property
    def sconfig(self) -> "Sconfig":
        """
        Récupérer le gestionnaire de configuration du serveur

        :return: Le gestionnaire de configuration du serveur
        """
        return self.get_cog("Sconfig")

    # Get use avatar ----------------------------------------------------------

    async def user_avatar_as(
        self,
        user: Union[discord.User, discord.Member],
        size=512,
    ):
        """
        Récupérer l'avatar d'un utilisateur au format PNG ou GIF

        :param user: L'utilisateur
        :param size: La taille de l'avatar
        :return: L'avatar
        """
        # the avatar always exist, returns the URL to the default one
        avatar = user.display_avatar.with_size(size)
        if avatar.is_animated():
            return avatar.with_format("gif")
        else:
            return avatar.with_format("png")

    # pylint: disable=arguments-differ
    async def get_prefix(self, bot, msg=None):
        """
        Récupérer le préfixe du bot pour un message donné

        :param msg: Le message
        :return: Le préfixe
        """

        return commands.when_mentioned(self, msg)

    async def get_command_mention(self, command_name: str):
        """
        Get how a command should be mentionned (either app-command mention or raw name)
        """
        if command := await self.fetch_app_command_by_name(command_name.split(' ')[0]):
            return f"</{command_name}:{command.id}>"
        if command := self.get_command(command_name):
            return f"`{command.qualified_name}`"
        logs.error(f"Trying to mention invalid command: {command_name}")
        return f"`{command_name}`"

    # pylint: disable=arguments-differ
    async def add_cog(self, cog: commands.Cog, icon=None, display_name=None):
        """
        Ajouter un cog au bot

        :param cog: Le cog à ajouter
        :param icon: L'icône du cog

        :return: None

        :raises TypeError: Le cog n'hérite pas de commands.Cog
        :raises CommandError: Une erreur est survenue lors du chargement
        """
        self.cog_icons.update({cog.qualified_name.lower(): icon})
        self.cog_display_names.update({cog.qualified_name.lower(): display_name})

        await super().add_cog(cog)
        for module in self.cogs.values():
            if not isinstance(cog, type(module)):
                if hasattr(module, "on_anycog_load"):
                    try:
                        module.on_anycog_load(cog)
                    # pylint: disable=broad-exception-caught
                    except BaseException:
                        logs.error("Error while adding a cog")

    def get_cog_display_name(self, cog_name):
        return self.cog_display_names.get(cog_name.lower())

    def get_cog_icon(self, cog_name):
        return self.cog_icons.get(cog_name.lower())
    
    def get_cog_display_name_with_icon(self, cog_name):
        return self.get_cog_icon(cog_name) + " " + self.get_cog_display_name(cog_name)

    async def remove_cog(self, cog: str):
        """
        Supprimer un cog du bot

        Toutes les commandes et listeners enregistrés par le cog seront supprimés

        :param cog: Le cog à supprimer
        :return: None
        """
        await super().remove_cog(cog)
        for module in self.cogs.values():
            if not isinstance(cog, type(module)):
                if hasattr(module, "on_anycog_unload"):
                    try:
                        module.on_anycog_unload(cog)
                    # pylint: disable=broad-exception-caught
                    except BaseException:
                        logs.error("Error while removing a cog")
