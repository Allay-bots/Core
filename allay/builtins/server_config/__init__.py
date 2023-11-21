
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

version = "0.0.1"
icon = "🎛️"
name = "Server Config"

# Cog -------------------------------------------------------------------------

async def setup(bot: allay.Bot):
    "Load cogs related to server configuration"
    logs.info(f"Loading {icon} {name} v{version}...")
    await bot.add_cog(ConfigCog(bot), icon=icon, display_name=name)
    await bot.add_cog(Sconfig(bot), icon=icon, display_name=name)
