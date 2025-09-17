from core import MyBot
from .events import Events

async def setup(bot: MyBot):
    await bot.add_cog(Events(bot))