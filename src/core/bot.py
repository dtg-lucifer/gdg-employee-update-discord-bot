import discord
from discord.ext import commands
import config
import asyncio
import time
from typing import Callable, Coroutine, List
from motor.motor_asyncio import AsyncIOMotorClient
import logging


startup_task: List[Callable[["MyBot"], Coroutine]] = []

class MyBot(commands.Bot):
    """Custom class inherited from commands.Bot"""

    def __init__(self, **kwargs):
        super().__init__(
            command_prefix = get_prefix,
            intents = discord.Intents.all(),
            **kwargs
            )
        
        self.uptime = None
        self.setup_logger()
        self.help_command = None

        self.prefix_cache = {}
        self.ping_cache = {"ping":"pong"}

    def boot(self):

        try:
            self.logger.info("Bot is booting....")
            super().run(token=config.bot.token)

        except Exception as e:
            self.logger.error("Bot shutting down....")
            self.logger.error(f"An error occurred: {e}\n")

    def setup_logger(self):
        self.logger = logging.getLogger(" ")
        self.logger.setLevel(logging.INFO)
        
        dt_fmt = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(
            "{asctime} {levelname:<8} {name} {message}", dt_fmt, style="{"
        )

        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        for logger_name in ('asyncio', 'wavelink', 'discord.voice_state'):
            logging.getLogger(logger_name).setLevel(logging.CRITICAL)


    async def load_cache(self):

        # Load prefix cache
        data = await self.db["prefix"].find({}).to_list()
        for entry in data:
            self.prefix_cache[entry["guild_id"]] = entry["prefix"]
        self.logger.info("Loaded prefix cache")

        self.logger.info("Loaded level cache")

    async def setup_hook(self):
        self.uptime = time.time()
        await asyncio.gather(*(task(self) for task in startup_task))
        await self.load_cache()

    global get_prefix
    async def get_prefix(self, message: discord.Message):

        prefixes = [config.bot.default_prefix]

        # no_prefix = await self.db["np"].find_one({"uid" : message.author.id})
        # guild_prefix = await self.db["prefix"].find_one({"guild_id" : message.guild.id})
        guild_prefix = self.prefix_cache.get(message.guild.id)
            

        if guild_prefix:
            prefixes.append(guild_prefix)

        # if no_prefix:
        #     prefixes.append("")

        return commands.when_mentioned_or(*prefixes)(self, message)
    
    @startup_task.append
    async def setup_db(self):
        try:
            self.db = AsyncIOMotorClient(config.database.token)[config.database.db_name]
            self.logger.info("Connected to database")

        except Exception as e:
            self.logger.error("Failed to load database")
            self.logger.error(e)

    @startup_task.append
    async def setup_cogs(self):
        for cog in config.bot.cogs:
            try:
                if cog == "jishaku":
                    await self.load_extension(cog)
                else:
                    await self.load_extension(f"cogs.{cog}")
                self.logger.info(f"Loaded {cog}")
            except Exception as e:
                self.logger.error(f"Failed to load: {cog}")
                self.logger.error(e)
        self.logger.info("Loaded all cogs")
