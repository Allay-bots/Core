
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
        
        prefix = BotConfig.get("core.default_prefix")

        return commands.when_mentioned_or(prefix)(self, msg)

    def db_query(
        self,
        query: str,
        args: Union[tuple, dict],
        *,
        fetchone: bool = False,
        returnrowcount: bool = False,
        astuple: bool = False,
    ) -> Union[int, List[dict], dict]:
        """
        Faire une requête à la base de données du bot

        Si SELECT, retourne une liste de résultats, ou seulement le premier résultat (si fetchone)
        Pour toute autre requête, retourne l'ID de la ligne affectée, ou le nombre de lignes
        affectées (si returnrowscount)

        :param query: La requête à faire
        :param args: Les arguments de la requête
        :param fetchone: Si la requête est un SELECT, retourne seulement le premier résultat
        :param returnrowcount: Si la requête est un INSERT, UPDATE ou DELETE, retourne le nombre
            de lignes affectées
        :param astuple: Si la requête est un SELECT, retourne les résultats sous forme de tuple
        :return: Le résultat de la requête
        """

        cursor = self.database.cursor()
        try:
            cursor.execute(query, args)
            if query.startswith("SELECT"):
                _type = tuple if astuple else dict
                if fetchone:
                    row = cursor.fetchone()
                    result = _type() if row is None else _type(row)
                else:
                    result = list(map(_type, cursor.fetchall()))
            else:
                self.database.commit()
                if returnrowcount:
                    result = cursor.rowcount
                else:
                    result = cursor.lastrowid
        except Exception as exception:
            cursor.close()
            raise exception
        cursor.close()
        return result

    @property
    def _(self) -> Callable[..., Awaitable[str]]:
        """Translate something
        
        :param context: The guild, channel or user for which to translate
        :param key: The key to translate
        :param kwargs: The arguments to pass to the translation

        :return: The translated string
        """
        cog = self.get_cog('Languages')
        if cog is None:
            logs.error("Unable to load Languages cog")
            return lambda *args, **kwargs: args[1]
        return cog.tr

    async def fetch_app_commands(self):
        "Populate the app_commands_list attribute from the Discord API"
        self.app_commands_list = await self.tree.fetch_commands(guild=None)

    async def fetch_app_command_by_name(self, name: str) -> Optional[discord.app_commands.AppCommand]:
        "Get a specific app command from the Discord API"
        if self.app_commands_list is None:
            await self.fetch_app_commands()
        for command in self.app_commands_list:
            if command.name == name:
                return command
        return None

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
