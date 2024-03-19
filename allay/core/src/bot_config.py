"""
Ce programme est régi par la licence CeCILL soumise au droit français et
respectant les principes de diffusion des logiciels libres. Vous pouvez
utiliser, modifier et/ou redistribuer ce programme sous les conditions
de la licence CeCILL diffusée sur le site "http://www.cecill.info".
"""

#==============================================================================
# Import requirements
#==============================================================================

# Standard libs ---------------------------------------------------------------

import importlib
import os
from typing import Any
import yaml

# Thrid party libs ------------------------------------------------------------

from LRFutils import color


#==============================================================================
# BotConfig class
#==============================================================================

accept = ("y", "yes", "yeah", "ye")
decline = ("n", "no", "nope", "nah")

class BotConfig:
    "Handle the bot general configuration"

    # Global variables --------------------------------------------------------

    __global_config: dict[str, dict[str, Any]] = {}

    # Loader ------------------------------------------------------------------

    @staticmethod
    def load(setup_if_missing: bool = False):
        "Check basic requirements and start the setup script if something is missing"

        plugin_path = "allay/plugins"
        builtins_path = "allay/builtins"
        config_file_exist = os.path.isfile("config.yaml")

        # Load config template
        with open("allay/core/data/default_bot_config.yaml", "r", encoding='utf-8') as file:
            BotConfig.__global_config.update(yaml.safe_load(file))

        # Load plugin config template
        for plugin in os.listdir(plugin_path):
            if os.path.isfile(file := plugin_path + "/" + plugin + "/config.yaml"):
                with open(file, encoding='utf-8') as file:
                    BotConfig.__global_config.update({"plugins":{plugin: yaml.safe_load(file)}})

        # Load builtins config template
        for builtin in os.listdir(builtins_path):
            if os.path.isfile(file := builtins_path + "/" + builtin + "/config.yaml"):
                with open(file, encoding='utf-8') as file:
                    BotConfig.__global_config.update({"builtins":{builtin: yaml.safe_load(file)}})

        # If a config already exist -> overwrite the templates
        if config_file_exist:
            with open("config.yaml", "r", encoding='utf-8') as file:
                BotConfig.__global_config.update(yaml.safe_load(file))

        # Overwrite config with env variables
        environment_used = False
        for key, value in os.environ.items():
            path = key.lower().split("_")
            if path[0] == "allay":
                environment_used = True
                config = BotConfig.__global_config
                for i in path[1:-1]:
                    config = config[i]
                config[path[-1]] = value

        # Run setup script if config is missing, but not if env variables are set
        # and setup_if_missing is False
        if (not config_file_exist) and (not environment_used) and setup_if_missing:
            BotConfig.setup()

        # Save
        BotConfig.save()


    @staticmethod
    def save():
        "Save the config file"
        with open("config.yaml", "w", encoding='utf-8') as file:
            yaml.dump(BotConfig.__global_config, file)

    # Environment -------------------------------------------------------------
    @staticmethod
    def is_token_environmentally_set():
        "Check if the token is set in the environment variables"
        return os.getenv("ALLAY_CORE_TOKEN") is not None

    # Setup -------------------------------------------------------------------

    @staticmethod
    def setup():
        # TODO
        pass

    # Accessor ----------------------------------------------------------------

    @staticmethod
    def get(config: str) -> Any:
        "Get the config value from a given configuration path"
        path = config.split(".")
        conf = BotConfig.__global_config
        for i in path:
            conf = conf[i]
        return conf

    #==============================================================================
    # Config setup script
    #==============================================================================

    @staticmethod
    def setup_plugins():
        """Run the "run" function of each plugin's "setup.py" file in order to allow user to
        configure the plugins.
        Called once in the main setup script."""

        for plugin in os.listdir("plugins"):
            if os.path.isfile("plugins/" + plugin + "/setup.py"):

                plugin_setup = importlib.import_module("plugins." + plugin + ".setup")

                choice = input(
                f"\n{color.fg.blue}🔌 Do you want to configure {plugin} plugin? [Y/n]:{color.stop} "
                )

                if choice.lower() not in decline:
                    plugin_config = plugin_setup.run()
                    if plugin_config is not None:
                        BotConfig.__global_config.update({plugin: plugin_config})

        # Save config
        BotConfig.save()


    #==============================================================================
    # Token Check
    #==============================================================================

    @staticmethod
    def token_set(force_set: bool = False):
        """Check if the token is set, if not, ask for it."""

        if BotConfig.get("core.token") is not None and not force_set:
            choice = input(
                f"\n🔑 {color.fg.blue}A token is already set."\
                    f"Do you want to edit it? [y/N]:{color.stop} "
            )
            if choice.lower() not in accept:
                return

        # pylint: disable=line-too-long
        print(
            f"""
    🔑 You need to set your Discord bot token in the config file.
    To do so, go on {color.fg.blue}https://discord.com/developers/applications{color.stop}, select your application, go in bot section and copy your token.
    To create a bot application, please refere to this page: {color.fg.blue}https://discord.com/developers/docs/intro{color.stop}.\n   Also, be sure to anable all intents."""
        )

        token = ""
        while token == "":
            token = input(f"\n🔑 {color.fg.blue}Your bot token:{color.stop} ")
            if token == "":
                print(f"\n{color.fg.red}🔑 You need to set a token.{color.stop}")
            else:
                BotConfig.__global_config["core"]["token"] = token

        BotConfig.save()

    #==============================================================================
    # Advanced setup
    #==============================================================================

    @staticmethod
    def advanced_setup():
        "Ask the user to set the bot admins and the error channel to use."

        # Admins

        error = True
        while error:
            error = False
            choice = input(
                f"\n{color.fg.blue}👑 Bot admins"\
                    f"(User ID separated with comma. Let empty to ignore):{color.stop} "
            )
            if choice != "":
                admins = choice.replace(" ", "").split(",")
                try:
                    BotConfig.__global_config["core"]["admins"] = [
                        int(admin_id) for admin_id in admins
                    ]
                except ValueError:
                    print(
                        f"{color.fg.red}👑 Invalid entry. Only user ID (integers),"\
                            f"comma and space are expected.{color.stop}"
                    )
                    error = True

        # Error channel

        error = True
        while error:
            error = False
            choice = input(
                f"\n{color.fg.blue}🤕 Error channel (Channel ID. Let empty to ignore):{color.stop} "
            )
            if choice != "":
                try:
                    channel = int(choice)
                    BotConfig.__global_config["core"]["error_channels"] = channel
                except ValueError:
                    print(
                        f"{color.fg.red}🤕 Invalid entry. Only channel ID (integers) are expected."\
                            f"{color.stop}"
                    )
                    error = True

        BotConfig.save()