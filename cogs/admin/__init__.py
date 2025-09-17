from core import MyBot
from .admin import Admin

async def setup(bot: MyBot):
    await bot.add_cog(Admin(bot))