from core import MyBot
from .level import Level

async def setup(bot: MyBot):
    await bot.add_cog(Level(bot))