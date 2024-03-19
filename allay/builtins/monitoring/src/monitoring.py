"""
Ce programme est régi par la licence CeCILL soumise au droit français et
respectant les principes de diffusion des logiciels libres. Vous pouvez
utiliser, modifier et/ou redistribuer ce programme sous les conditions
de la licence CeCILL diffusée sur le site "http://www.cecill.info".
"""

import time

import aiohttp
from discord.ext import tasks, commands
from LRFutils import logs

import allay


class MonitoringCog(commands.Cog):
    def __init__(self, bot: allay.Bot):
        self.bot = bot
        self.error_counter = 0
        self.session = aiohttp.ClientSession()

    async def cog_load(self) -> None:
        if allay.BotConfig.get("builtins.monitoring.enabled") is True:
            for i in range(5):
                if await self.ping_monitoring():
                    logs.info("Monitoring test ping successful")
                    logs.info("Monitoring enabled")
                    self.loop.start()  # pylint: disable=no-member
                    return
                logs.error("Monitoring ping failed %s times", i + 1)
                time.sleep(5)
            self.bot.dispatch(
                "error", RuntimeError("Monitoring disabled due to ping failure")
            )

    async def ping_monitoring(self):
        # retrieve Discord Ping
        ping = round(self.bot.latency * 1000, 0)

        # build URL
        url = (
                allay.BotConfig.get("builtins.monitoring.push_url")
                + allay.BotConfig.get("builtins.monitoring.push_monitor")
                + "?status=up&msg=OK&ping="
                + str(ping)
        )

        # send request
        async with self.session.get(url) as resp:
            if resp.status != 200:
                logs.error("Monitoring ping failed with status %s", resp.status)
                return False
            json = await resp.json()
            try:
                if not json["ok"]:
                    logs.error(
                        "Monitoring ping failed with error : %s", json["msg"]
                    )
                    return False
                return True
            except KeyError:
                logs.error("Monitoring ping failed")
                return False

    @tasks.loop(seconds=20)
    async def loop(self):
        if await self.ping_monitoring():
            self.error_counter = 0
            return
        self.error_counter += 1
        if self.error_counter >= 6:
            self.bot.dispatch(
                "error",
                RuntimeError("Monitoring disabled due to multiple ping failure"),
            )
            self.loop.stop()  # pylint: disable=no-member

    @loop.before_loop
    async def before_ping_monitoring(self):
        await self.bot.wait_until_ready()
