from core import MyBot
from .help import Help

async def setup(bot: MyBot):
    await bot.add_cog(Help(bot))