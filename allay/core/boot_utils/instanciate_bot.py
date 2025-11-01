import asyncio

import art
import discord
import logging

import allay
from allay.core.src.discord import Bot

logger = logging.getLogger(__name__)


def instanciate_bot():
    "Create the bot instance and returns it"
    allay.BotConfig.load()
    # check if a token is set
    if allay.BotConfig.get("core.token") is None:
        allay.core.BotConfig.token_set(force_set=True)

    allay.Database.load()

    bot = Bot(
        database=allay.Database.database,
        case_insensitive=True,
        status=discord.Status.do_not_disturb,
    )

    print(" ")
    logger.info(f"▶️ Starting Allay Core v{allay.core.__version__}...")
    print(" ")
    print(art.text2art(f"Allay v{allay.core.__version__}",font='small',chr_ignore=True))

    # On Discord Bot ready -----------------------------------------------------

    @bot.listen()
    async def on_ready():
        await on_bot_ready(bot)
         # only load plugins once
        bot.remove_listener(on_ready)

    return bot


async def on_bot_ready(bot: Bot):
    "Print bot informations and load plugins when connection to discord is established"

    # Show bot informations ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    logger.info("✅ Bot connected")
    if bot.user:
        logger.info(f"Username: {bot.user.name}")
        logger.info(f"User ID: {bot.user.id}")
    else:
        logger.info("No user connected")

    if len(bot.guilds) < 20:
        logger.info(f"Connected on {len(bot.guilds)} server:\n - " +
                '\n - '.join(x.name for x in bot.guilds))
    else:
        logger.info(f"Connected on {len(bot.guilds)} server")

    # Load plugins ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    print(" ")
    await load_builtins(bot)

    print(" ")
    await load_plugins(bot)

    # Sync app commands ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    logger.info("♻️ Syncing app commands...")
    try:
        await bot.tree.sync()
    except discord.DiscordException as e:
        logger.error("⚠️ Error while syncing app commands: %s", repr(e))
    else:
        logger.info("✅ App commands synced")

    print("--------------------------------------------------------------------------------")

    await bot.change_presence(status=discord.Status.online)
    await asyncio.sleep(2)

async def load_builtins(bot: Bot):
    "Load builtins modules"
    loaded = 0
    failed = 0
    notloaded = ""
    logger.info("📦 Loading builtins...")

    for extension in allay.builtins.all_modules:
        try:
            await bot.load_extension("allay.builtins." + extension)
            loaded += 1
        except Exception as exc:  # pylint: disable=broad-except
            logger.error(f"Failed to load extension: {extension}\n{exc}")
            notloaded += "\n - " + extension
            failed += 1

    logger.info(f"{loaded} builtins loaded, {failed} builtins failed")

async def load_plugins(bot: Bot):
    "Load installed plugins"
    loaded = 0
    failed = 0
    notloaded = ""

    logger.info("🔌 Loading plugins...")

    for extension in allay.plugins.all_modules:
        try:
            await bot.load_extension("allay.plugins." + extension)
            loaded += 1
        except Exception as exc:  # pylint: disable=broad-except
            logger.error(f"Failed to load extension: {extension}\n{exc}")
            notloaded += "\n - " + extension
            failed += 1

    logger.info(f"{loaded} plugins loaded, {failed} plugins failed")
