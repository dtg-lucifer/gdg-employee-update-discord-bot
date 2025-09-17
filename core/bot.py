import discord
from discord.ext import commands
import config
import asyncio
import time
from typing import Callable, Coroutine, List
import wavelink
from motor.motor_asyncio import AsyncIOMotorClient
import logging
from core.api import set_bot_instance


startup_task: List[Callable[["MyBot"], Coroutine]] = []
class MyBot(commands.Bot):
    """Custom class inherited from commands.Bot"""

    def __init__(self, **kwargs):
        super().__init__(
            command_prefix = get_prefix,
            # intents = discord.Intents(guilds = True),
            intents = discord.Intents.all(),
            owner_ids = config.bot.owner_ids,
            case_insensitive = True,
            **kwargs
            )
        
        self.uptime = None
        self.nodes: List[wavelink.Node] = []
        self.setup_logger()
        self.help_command = None

        self.prefix_cache = {}
        self.ping_cache = {"ping":"pong"}
        self.autoresponder_cache = {}
        self.level_cache = {}
        self.premium_cache = {}
        self.np_cache = {}
        self.gifignore_cache = {}

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

        # Load autoresponder cache
        data = await self.db["autoresponder"].find({}).to_list()
        for entry in data:
            guild_id = entry["guild_id"]
            
            if guild_id not in self.autoresponder_cache:
                self.autoresponder_cache[guild_id] = []
            self.autoresponder_cache[guild_id].append({
                "trigger": entry["trigger"],
                "responce": entry["responce"],
                "matchmode": entry["matchmode"]
            })
        self.logger.info("Loaded autoresponder cache")

        # load np cache
        data = await self.db["np"].find({}).to_list()
        for entry in data:
            self.np_cache[entry["uid"]] = "np"

        # Load level cache

        # self.logger.info("Loaded level cache")

        # #load premuim cache
        # data = await self.db["premium"].find({}).to_list()
        # for entry in data:
        #     user_id = entry["user_id"]
        #     if user_id not in self.premium_cache:
        #         self.premium_cache[user_id] = []
        #     self.level_cache[user_id].append({
        #         "expires_at": entry["expires_at"]
        #     })

        # load gif ignore cache
        data = await self.db["gifignore"].find({}).to_list()
        for entry in data:
            self.gifignore_cache[entry["guild_id"]] = entry["channels"]
        self.logger.info("Loaded gif ignore cache")

    async def setup_hook(self):
        self.uptime = time.time()
        await asyncio.gather(*(task(self) for task in startup_task))
        await self.load_cache()
        set_bot_instance(self)

    global get_prefix
    async def get_prefix(self, message: discord.Message):

        prefixes = []

        np_prefix = self.np_cache.get(message.author.id)
        if message.guild is None:
            prefixes.append(config.bot.default_prefix)
            if np_prefix:
                prefixes.append("")
        else:
            guild_prefix = self.prefix_cache.get(message.guild.id)
            if guild_prefix:
                prefixes.append(guild_prefix)
            else:
                prefixes.append(config.bot.default_prefix)
            if np_prefix:
                prefixes.append("")


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


    @startup_task.append
    async def setup_wavelink(self):
        # await asyncio.sleep(5)
        
        for i, node in enumerate(config.lavalink.nodes, start=1):
            uri = "ws://{}:{}".format(node.get("host"), node.get("port"))

            node_config = wavelink.Node(
                identifier= f"Node {i}",
                uri=uri,
                password=node.get("auth"),
                client=self,
                retries=3,
            )
            
            try:
                await wavelink.Pool.connect(client=self, nodes=[node_config])
                self.nodes.append(node_config)
                self.logger.info(f"Connected to {node_config.identifier}")
            except Exception as e:
                self.logger.error(f"Failed to connect to node {i}: {e}")