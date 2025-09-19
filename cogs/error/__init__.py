from core import MyBot
from .error import Error

async def setup(bot: MyBot):
    await bot.add_cog(Error(bot))