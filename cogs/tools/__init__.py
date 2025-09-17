from core import MyBot
from .tools import Tools

async def setup(bot: MyBot):
    await bot.add_cog(Tools(bot))