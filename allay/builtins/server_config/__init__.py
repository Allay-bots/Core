
#==============================================================================
# Requirements
#==============================================================================

# Standard libs ---------------------------------------------------------------

# Third party libs ------------------------------------------------------------

from LRFutils import logs

# Project modules -------------------------------------------------------------

import allay
from .src.config_manager import *
from .src.sconfig import *

#==============================================================================
# Plugin
#==============================================================================

# Info ------------------------------------------------------------------------

VERSION = "0.0.1"
ICON = "🎛️"
NAME = "Server Config"

# Cog -------------------------------------------------------------------------

async def setup(bot: allay.Bot):
    "Load cogs related to server configuration"
    logs.info(f"Loading {ICON} {NAME} v{VERSION}...")
    await bot.add_cog(ConfigCog(bot), icon=ICON, display_name=NAME)
    await bot.add_cog(Sconfig(bot), icon=ICON, display_name=NAME)
