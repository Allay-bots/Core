#!/usr/bin/env python
# coding=utf-8

"""
Ce programme est régi par la licence CeCILL soumise au droit français et
respectant les principes de diffusion des logiciels libres. Vous pouvez
utiliser, modifier et/ou redistribuer ce programme sous les conditions
de la licence CeCILL diffusée sur le site "http://www.cecill.info".
"""

# ==============================================================================
# Check & import requirements
# ==============================================================================

# Standard libs ---------------------------------------------------------------

import logging
import os
import sys

from allay.core.boot_utils.check_requirements import check_requirements

check_requirements()

# Thrid party libs ------------------------------------------------------------

import discord

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

import allay
from allay.core.boot_utils.instanciate_bot import instanciate_bot

# ==============================================================================
# START
# ==============================================================================

bot = instanciate_bot()

# Launch bot
try:
    bot.run(
        allay.BotConfig.get("core.token"),
        log_handler=logging.StreamHandler(sys.stdout)
    )
except discord.errors.LoginFailure:
    logger.error("⚠️ Invalid token")
    if not allay.BotConfig.is_token_environmentally_set():
        allay.BotConfig.token_set(force_set=True)
        os.system("python3 start.py")
    else:
        logger.warning("⚠️ Token is set as an environment variable. Please check your .env file for ALLAY_CORE_TOKEN "
                       "variable.")
    sys.exit()
