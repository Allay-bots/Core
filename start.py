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
import pkg_resources # deprecated, use importlib.resources instead
import asyncio
import sqlite3
import logging

# Check python version --------------------------------------------------------

py_version = sys.version_info
if py_version.major != 3 or py_version.minor < 10:
    print("⚠️ \033[33mGipsy require Python 3.10 or more.\033[1m")
    sys.exit(1)

# Check installed modules -----------------------------------------------------

# TODO : update this
with open("requirements.txt", "r", encoding='utf-8') as file:
    packages = pkg_resources.parse_requirements(file.readlines())
try:
    pkg_resources.working_set.resolve(packages)
except pkg_resources.VersionConflict as exc:
    print("\n🤕 \033[31mOops, there is a problem in the dependencies.\033[0m")
    print(f"\n⚠️ \033[33m{type(exc).__name__}: {exc}\033[0m\n ")
    print(f"\n\n Please run \"pip install -r requirements.txt\"")
except Exception as exc: # pylint: disable=broad-exception-caught
    print("\n🤕 \033[31mOops, there is a problem in the dependencies.\033[0m")
    print(f"\n⛔ \u001b[41m\u001b[37;1m{type(exc).__name__}\033[0m: \033[31m{exc}\033[0m\n")
    print(f"\n\n Please run \"pip install -r requirements.txt\"")

# Thrid party libs ------------------------------------------------------------

import discord
from LRFutils import color, logs
import art

# Project modules -------------------------------------------------------------

import allay

#==============================================================================
# START
#==============================================================================

allay.BotConfig.load()
allay.Database.load()

bot = allay.core.discord.Bot(
    case_insensitive=True,
    status=discord.Status.do_not_disturb,
    database=allay.Database.database,
)

print(" ")
logs.info(f"▶️ Starting Allay Core v{allay.core.version}...")
print(" ")
print(art.text2art(f"Allay v{allay.core.version}",font='small',chr_ignore=True))

# On Discord Bot ready -----------------------------------------------------

async def on_ready():

    # Show bot informations ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    logs.info(color.green("✅ Bot connected"))
    logs.info(f"Nom : {bot.user.name}")
    logs.info(f"ID : {bot.user.id}")

    if len(bot.guilds) < 20:
        logs.info(f"Connected on {len(bot.guilds)} server:\n - " + '\n - '.join([x.name for x in bot.guilds]))
    else:
        logs.info(f"Connected on {len(bot.guilds)} server")

    # Load plugins ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    loaded = 0
    failed = 0
    notloaded = ""

    print(" ")
    
    logs.info("📦 Loading builtins...")

    for extension in allay.builtins.all:
        try:
            await bot.load_extension("allay.builtins." + extension)
            loaded += 1
        except Exception as exc:  # pylint: disable=broad-except
            logs.error(f"Failed to load extension: {extension}\n{exc}")
            notloaded += "\n - " + extension
            failed += 1
    
    logs.info(f"{loaded} builtins loaded, {failed} builtins failed")

    loaded = 0
    failed = 0
    notloaded = ""

    print(" ")
    logs.info("🔌 Loading plugins...")

    for extension in allay.plugins.all:
        try:
            await bot.load_extension("allay.plugins." + extension)
            loaded += 1
        except Exception as exc:  # pylint: disable=broad-except
            logs.error(f"Failed to load extension: {extension}\n{exc}")
            notloaded += "\n - " + extension
            failed += 1

    logs.info(f"{loaded} plugins loaded, {failed} plugins failed")
    print(" ")

    # Sync app commands ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    logs.info("♻️ Syncing app commands...")
    try:
        await bot.tree.sync()
    except discord.DiscordException as e:
        logs.error("⚠️ Error while syncing app commands: %s", repr(e))
    else:
        logs.info("✅ App commands synced")

    print("--------------------------------------------------------------------------------")

    await bot.change_presence(status=discord.Status.online)
    await asyncio.sleep(2)

    # only load plugins once
    bot.remove_listener(on_ready)

bot.add_listener(on_ready)

# Launch bot
try:
    bot.run(
        allay.core.BotConfig.get("core.token"),
        log_handler=logging.StreamHandler(sys.stdout)
    )
except discord.errors.LoginFailure:
    logs.error("⚠️ Invalid token")
    allay.core.BotConfig.token_set(force_set=True)
    os.system("python3 start.py")
    exit()