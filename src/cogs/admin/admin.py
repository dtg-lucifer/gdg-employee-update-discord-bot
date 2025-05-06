import discord
from discord.ext import commands
import config
from core.cog import Cog
from main import MyBot
from typing import Optional


class Admin(Cog):
    def __init__(self, bot: MyBot):
        self.bot=bot
        self.emoji = config.emoji.cog_admin

    @commands.hybrid_command(name = "prefix", description = "Set a custom prefix for your guild")
    @commands.guild_only()
    async def prefix (self, ctx: commands.Context, prefix: Optional[str]):
        if not prefix:
            prefix = self.bot.prefix_cache.get(ctx.guild.id)
            if not prefix:
                prefix = config.bot.default_prefix

            return await ctx.send(embed=discord.Embed(
                title = "Current Prefix",
                description = f"Current prefix is `{prefix}`",
                color = config.color.no_color
            ))
        if ctx.author.guild_permissions.administrator == False:
            return await ctx.send("You need `Administrator` permission to set prefix")
        
        await self.bot.db["prefix"].update_one(
        {"guild_id": ctx.guild.id}, {"$set": {"guild_id": ctx.guild.id, "prefix": prefix}}, upsert=True)
        self.bot.prefix_cache[ctx.guild.id] = prefix
        await ctx.send(f"**Success: ** Server prefix is now `{prefix}`")

    
