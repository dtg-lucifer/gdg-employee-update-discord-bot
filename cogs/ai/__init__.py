from core import MyBot
from .ai import ArtificialIntelligence

async def setup(bot: MyBot):
    await bot.add_cog(ArtificialIntelligence(bot))