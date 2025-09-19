from core import MyBot
from .autoresponder import AutoResponder

async def setup(bot: MyBot):
    await bot.add_cog(AutoResponder(bot))