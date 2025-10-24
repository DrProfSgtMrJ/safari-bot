import os
import logging
from dotenv import load_dotenv
from discord import Intents
from discord.ext import commands

from cogs.safari import SafariCog

load_dotenv()

logger_handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

async def main():
    async with bot:
        await bot.add_cog(SafariCog(bot))
        await bot.start(token=DISCORD_TOKEN) 


if __name__ == "__main__":
    import asyncio

    logging.basicConfig(level=logging.DEBUG, handlers=[logger_handler])
    asyncio.run(main())
