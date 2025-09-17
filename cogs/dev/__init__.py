from core import MyBot
from .dev import Dev

async def setup(bot: MyBot):
    await bot.add_cog(Dev(bot))