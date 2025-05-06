from discord.ext.commands import Cog
from core.bot import MyBot

class Cog(Cog):
    def __init__(self, bot: MyBot):
        self.bot = bot

class Setup(Cog):
    def __init__(self, cog: Cog):
        self.cog = cog
        self.bot.add_cog(self.cog)
