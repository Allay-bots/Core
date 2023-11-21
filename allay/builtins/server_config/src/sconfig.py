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

from typing import Any, Optional, Sequence

# Third party libs ------------------------------------------------------------

import discord
import emoji
from discord.ext import commands

# Project modules -------------------------------------------------------------

import allay

# pylint: disable=relative-beyond-top-level
from .config_manager import CONFIG_OPTIONS, ConfigOption


#==============================================================================
# Plugin
#==============================================================================

class Sconfig(commands.Cog):
    "Allow guild admins to edit the bot configuration in their server"

    def __init__(self, bot: allay.Bot):
        self.bot = bot
        self.file = "sconfig"
        self.sorted_options: dict[str, dict[str, ConfigOption]] = {}  # config options sorted by cog
        self.config_options: list[str] = []
        for cog in bot.cogs.values():
            self._add_options_from_cog(cog)
        # for whatever reason, the for loop above doesn't include its own cog,
        # so we just force it
        self.sorted_options[self.__cog_name__] = {
            k: v for k, v in CONFIG_OPTIONS.items() if k in self.config_options
        }

    def on_anycog_load(self, cog: commands.Cog):
        """Used to enable config commands when a cog is enabled

        Parameters
        -----------
        cog: :class:`commands.Cog`
            The cog which got enabled"""
        self._add_options_from_cog(cog)
        for opt in self.sorted_options[cog.__cog_name__].values():
            # we enable the commands if needed
            if (command_name := opt.get("command")) and (
                command := self.bot.get_command("config " + command_name)):
                command.enabled = True

    def on_anycog_unload(self, cog: str):
        """Used to disable config commands when a cog is disabled

        Parameters
        -----------
        cog: :class:`str`
            The name of the disabeld cog"""
        if cog in self.sorted_options:
            for opt in self.sorted_options[cog].values():
                # we disable the commands if needed
                if (command_name := opt.get("command")) and (
                    command := self.bot.get_command("config " + command_name)):
                    command.enabled = True
            del self.sorted_options[cog]

    def _add_options_from_cog(self, cog: commands.Cog):
        "Append the cog-related configuration to the config options"
        if not hasattr(cog, "config_options"):
            # if the cog doesn't have any specific config
            return
        if not isinstance(cog.config_options, dict): # type: ignore
            raise TypeError("config_options must be a dict of config_name -> ConfigOption")
        self.sorted_options[cog.__cog_name__] = {
            k: v for k, v in CONFIG_OPTIONS.items() if k in cog.config_options # type: ignore
        }

    async def edit_config(self, guild_id: int, key: str, value: Any):
        """Edit or reset a config option for a guild

        Parameters
        -----------
        guild_id: :class:`int`
            The ID of the concerned guild

        key: :class:`str`
            The name of the option to edit

        value: :class:`Any`
            The new value of the config, or None to reset"""
        if value is None:
            del self.bot.server_configs[guild_id][key]
            return allay.I18N.tr(guild_id, "sconfig.option-reset", opt=key)
        try:
            self.bot.server_configs[guild_id][key] = value
        except ValueError:
            return allay.I18N.tr(guild_id, "sconfig.option-notfound", opt=key)
        return allay.I18N.tr(guild_id, "sconfig.option-edited", opt=key)

    async def format_config(self, guild: discord.Guild, key: str,
                            value: int | str | list[int] | list[str] | bool,
                            mention: bool = True) -> Optional[str]:
        "Format a configuration value in a nice human-readable string"
        if value is None:
            return None
        config = CONFIG_OPTIONS[key]

        def getname(x: discord.Role | discord.abc.GuildChannel):
            return x.mention if mention else x.name

        sep = " " if mention else " | "
        if key == "levelup_channel":
            if value in (None, "none", "any"):
                return str(value).capitalize()
        if config["type"] == "roles":
            if not isinstance(value, list) or not all(isinstance(x, int) for x in value):
                raise ValueError("Invalid value for roles config")
            roles = [guild.get_role(int(x)) for x in value]
            roles = [getname(x) for x in roles if x is not None]
            return sep.join(roles)
        if config["type"] == "channels":
            if not isinstance(value, list) or not all(isinstance(x, int) for x in value):
                raise ValueError("Invalid value for roles config")
            channels = [guild.get_channel(int(x)) for x in value]
            channels = [getname(x) for x in channels if x is not None]
            return sep.join(channels)
        if config["type"] == "categories":
            if not isinstance(value, list) or not all(isinstance(x, int) for x in value):
                raise ValueError("Invalid value for roles config")
            categories = [guild.get_channel(int(x)) for x in value]
            categories = [x.name for x in categories if x is not None]
            return " | ".join(categories)
        if config["type"] == "emojis":

            def emojis_convert(s_emoji: str, bot_emojis: Sequence[discord.Emoji]) -> str:
                if s_emoji.isnumeric():
                    if d_em := discord.utils.get(bot_emojis, id=int(s_emoji)):
                        return f":{d_em.name}:"
                    return ":deleted_emoji:"
                return emoji.emojize(s_emoji, language="alias")

            if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
                raise ValueError("Invalid value for roles config")
            return " ".join(emojis_convert(str(x), self.bot.emojis) for x in value)
        if config["type"] == "int":
            if not isinstance(value, int):
                raise ValueError("Invalid value for int config")
            return str(value)
        return str(value)

    @commands.group(name="config")
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def main_config(self, ctx: allay.Context):
        """Edit your server configuration"""
        if ctx.guild is None: # type guard (shouldn't happen)
            return
        if ctx.subcommand_passed is None:
            # get the server config
            config = ctx.bot.server_configs[ctx.guild.id]

            # get the length of the longest key to align the values in columns
            max_key_length = 0
            max_value_length = 0
            for options in self.sorted_options.values():
                configs_len = [len(k) for k in config.keys() if k in options]
                max_key_length = (
                    max(max_key_length, *configs_len)
                    if len(configs_len) > 0
                    else max_key_length
                )
                values_len = [
                    len(str(await self.format_config(ctx.guild, k, v, mention=False)))
                    for k, v in config.items()
                    if k in options
                ]
                max_value_length = (
                    max(max_value_length, *values_len)
                    if len(values_len) > 0
                    else max_value_length
                )
            max_key_length += 3
            max_value_length += 1

            # iterate over modules
            cpt = 0
            embeds = []
            for module, options in sorted(self.sorted_options.items()):

                subconf = {k: v for k, v in config.items() if k in options}
                if len(subconf) == 0:
                    continue

                module_config = ""

                # iterate over configs for that group
                for k, v in subconf.items():
                    value = await self.format_config(ctx.guild, k, v, False)
                    module_config += (
                        (f"{k}:").ljust(max_key_length)
                        + f" {value}".ljust(max_value_length)
                        + "\n"
                    )

                if hasattr(self.bot.get_cog(module), "_create_config"):
                    for extra in await self.bot.get_cog(module)._create_config(ctx): # type: ignore # pylint: disable=protected-access
                        module_config += (
                            (f"[{extra[0]}]").ljust(max_key_length)
                            + f" {extra[1]}".ljust(max_value_length)
                            + "\n"
                        )

                # Put the config in embeds and stack them to be send in group
                embeds.append(
                    discord.Embed(
                        title=self.bot.get_cog_display_name_with_icon(module),
                        description=f"```yml\n{module_config}```",
                        colour=0x2F3136,
                    )
                )

                cpt += 1

                # Send the config by group of 10 (limit of embed number per message)
                if cpt % 10 == 0:
                    await ctx.send(embeds=embeds)
                    embeds = []

            # Send the remaining embeds
            if cpt % 10 != 0:
                await ctx.send(embeds=embeds)

        elif ctx.invoked_subcommand is None:
            await ctx.send(allay.I18N.tr(ctx.guild.id, "sconfig.option-notfound"))
