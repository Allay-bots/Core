#!/usr/bin/env python
# coding=utf-8

"""
Ce programme est régi par la licence CeCILL soumise au droit français et
respectant les principes de diffusion des logiciels libres. Vous pouvez
utiliser, modifier et/ou redistribuer ce programme sous les conditions
de la licence CeCILL diffusée sur le site "http://www.cecill.info".
"""

#==============================================================================
# Check & import requirements
#==============================================================================

# Standard libs ---------------------------------------------------------------

import sys
import os
import pkg_resources
import asyncio
import sqlite3

# Check python version --------------------------------------------------------

py_version = sys.version_info
if py_version.major != 3 or py_version.minor < 10:
    print("⚠️ \033[33mGipsy require Python 3.10 or more.\033[1m")
    sys.exit(1)

# Check installed modules -----------------------------------------------------

with open("requirements.txt", "r", encoding='utf-8') as file:
    packages = pkg_resources.parse_requirements(file.readlines())
try:
    pkg_resources.working_set.resolve(packages)
except pkg_resources.VersionConflict as exc:
    print("\n🤕 \033[31mOops, there is a problem in the dependencies.\033[0m")
    print(f"\n⚠️ \033[33m{type(exc).__name__}: {exc}\033[0m\n ")
except Exception as exc: # pylint: disable=broad-exception-caught
    print("\n🤕 \033[31mOops, there is a problem in the dependencies.\033[0m")
    print(f"\n⛔ \u001b[41m\u001b[37;1m{type(exc).__name__}\033[0m: \033[31m{exc}\033[0m\n")

# Thrid party libs ------------------------------------------------------------

import discord
from LRFutils import color, logs
import art

# Project modules -------------------------------------------------------------

import allay

#==============================================================================
# START
#==============================================================================

allay.core.BotConfig.load()

# Creating client
client = allay.core.DiscordClient(
    case_insensitive=True,
    status=discord.Status.do_not_disturb,
    beta=False,
    database=allay.database,
)

print(" ")
logs.info(f"▶️ Starting Allay v{allay.core.version}...")
print(" ")
print(art.text2art(f"Allay v{allay.core.version}",font='small',chr_ignore=True))

# Loading extensions (global system + plugins)
async def load(bot_client, global_system_list, plugin_list):
    loaded = 0
    failed = 0
    notloaded = ""
    for extension in global_system_list + plugin_list:
        try:
            await bot_client.load_extension(extension)
            loaded += 1
        except Exception as exc:  # pylint: disable=broad-except
            client.log.error(
                "Failed to load extension: %s",
                extension,
                exc_info=exc,
            )
            notloaded += "\n - " + extension
            failed += 1
    return loaded, failed

# Printing info when the bot is started
async def on_ready():
    """Called when the bot is connected to Discord API"""
    client.log.info("%s✅ Bot connected", color.fg.green)
    client.log.info("Nom : %s", client.user.name)
    client.log.info("ID : %i", client.user.id)
    if len(client.guilds) < 200:
        servers = [x.name for x in client.guilds]
        client.log.info(
            "Connected on %i server:\n - %s",
            len(client.guilds),
            "\n - ".join(servers),
        )
    else:
        client.log.info("Connected on %i server", len(client.guilds))
    loaded, failed = await load(client, allay.builtins.all, allay.plugins.all)
    client.log.info(
        "%i plugins loaded, %i plugins failed",
        loaded,
        failed,
    )

    # Syncing slash commands
    client.log.info("♻️ Syncing app commands...")
    try:
        await client.tree.sync()
    except discord.DiscordException as e:
        client.log.error("⚠️ Error while syncing app commands: %s", repr(e))
    else:
        client.log.info("✅ App commands synced")

    print(
        "--------------------------------------------------------------------------------"
    )
    await client.change_presence(
        status=discord.Status.online,
    )
    await asyncio.sleep(2)

    # only load plugins once
    client.remove_listener(on_ready)

client.add_listener(on_ready)

# Launch bot
try:
    client.run(
        allay.core.BotConfig.get("core.token"),
        log_handler=None,
    )
except discord.errors.LoginFailure:
    client.log.error("⚠️ Invalid token")
    allay.core.BotConfig.token_set(force_set=True)
    os.system("python3 start.py")
    exit()