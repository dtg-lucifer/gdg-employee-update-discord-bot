from core import MyBot
from .minecraft import Minecraft

async def setup(bot: MyBot):
    await bot.add_cog(Minecraft(bot))