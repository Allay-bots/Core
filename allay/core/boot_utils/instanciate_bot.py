import asyncio

import art
import discord
from LRFutils import color, logs

import allay
from allay.core.src.discord import Bot


def instanciate_bot():
    "Create the bot instance and returns it"
    allay.BotConfig.load()
    allay.Database.load()

    bot = Bot(
        case_insensitive=True,
        status=discord.Status.do_not_disturb,
        database=allay.Database.database,
    )

    print(" ")
    logs.info(f"▶️ Starting Allay Core v{allay.core.__version__}...")
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

    logs.info(color.green("✅ Bot connected"))
    if bot.user:
        logs.info(f"Username: {bot.user.name}")
        logs.info(f"User ID: {bot.user.id}")
    else:
        logs.info("No user connected")

    if len(bot.guilds) < 20:
        logs.info(f"Connected on {len(bot.guilds)} server:\n - " +
                '\n - '.join(x.name for x in bot.guilds))
    else:
        logs.info(f"Connected on {len(bot.guilds)} server")

    # Load plugins ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    print(" ")
    await load_builtins(bot)

    print(" ")
    await load_plugins(bot)

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

async def load_builtins(bot: Bot):
    "Load builtins modules"
    loaded = 0
    failed = 0
    notloaded = ""
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

async def load_plugins(bot: Bot):
    "Load installed plugins"
    loaded = 0
    failed = 0
    notloaded = ""

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
