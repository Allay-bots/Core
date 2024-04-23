
#==============================================================================
# Import requirements
#==============================================================================

# Standard libs ---------------------------------------------------------------

import sqlite3
from typing import Optional, Union, TYPE_CHECKING

# Thrid party libs ------------------------------------------------------------

import discord
from discord.ext import commands
from LRFutils import logs

if TYPE_CHECKING:
    from allay.builtins.server_config import Sconfig, ConfigManager

# Project modules -------------------------------------------------------------

from allay.core.src.discord.context import Context

#==============================================================================
# Bot class
#==============================================================================

class Bot(commands.bot.AutoShardedBot):
    "Custom class for our bot"

    instances = []

    def __init__(
            self,
            database: sqlite3.Connection,
            case_insensitive: Optional[bool] = None,
            status: Optional[discord.Status] = None,
        ):
        intents = discord.Intents.default()
        intents.presences = True
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix=lambda bot, msg: self.get_prefix(msg),
            case_insensitive=case_insensitive,
            status=status,
            allowed_mentions=discord.AllowedMentions(everyone=False, roles=False),
            intents=intents,
        )

        self.database = database
        self.database.row_factory = sqlite3.Row
        self.cog_icons: dict[str, Optional[str]] = {}
        self.cog_display_names: dict[str, Optional[str]] = {}
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
    def server_configs(self) -> "ConfigManager":
        """
        Récupérer la configuration du serveur

        :return: La configuration du serveur
        """
        return self.get_cog("ConfigCog").conf_manager # type: ignore

    @property
    def sconfig(self) -> "Sconfig":
        """
        Récupérer le gestionnaire de configuration du serveur

        :return: Le gestionnaire de configuration du serveur
        """
        return self.get_cog("Sconfig") # type: ignore

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
        return avatar.with_format("png")

    async def get_prefix(self, _msg: discord.Message):
        """
        Retrieves the prefix the bot is listening to (only the bot mention here)

        :param msg: The context message
        :return: A list of usable prefixes
        """
        if self.user is None:
            return []
        return [f'<@{self.user.id}> ', f'<@!{self.user.id}> ']

    async def fetch_app_commands(self):
        "Populate the app_commands_list attribute from the Discord API"
        self.app_commands_list = await self.tree.fetch_commands()

    async def fetch_app_command_by_name(self, name: str):
        "Get a specific app command from the Discord API"
        if self.app_commands_list is None:
            await self.fetch_app_commands()
        if self.app_commands_list is None:
            raise RuntimeError("App commands list is still None")
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
    async def add_cog(self, cog: commands.Cog, icon: Optional[str] = None,
                      display_name: Optional[str] = None):
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
                        module.on_anycog_load(cog) # type: ignore
                    # pylint: disable=broad-exception-caught
                    except BaseException as err:
                        logs.error(f"Error while calling on_anycog_load: {err}")

    def get_cog_display_name(self, cog_id: str):
        "Get the display name of a given cog"
        return self.cog_display_names.get(cog_id.lower())

    def get_cog_icon(self, cog_id: str):
        "Get the icon of a given cog"
        return self.cog_icons.get(cog_id.lower())

    def get_cog_display_name_with_icon(self, cog_id):
        "Get the display name of a given cog with its icon"
        name = self.get_cog_display_name(cog_id) or cog_id
        if icon := self.get_cog_icon(cog_id):
            return icon + " " + name
        return name

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
                        module.on_anycog_unload(cog) # type: ignore
                    # pylint: disable=broad-exception-caught
                    except BaseException as err:
                        logs.error(f"Error while calling on_anycog_unload: {err}")
