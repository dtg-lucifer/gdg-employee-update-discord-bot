import discord
from discord.ext import commands, tasks
from core.cog import Cog
from core.bot import MyBot
import config
import time
import asyncio
from typing import cast
import aiohttp

class Events(Cog):
    def __init__(self, bot: MyBot):
        self.bot = bot
        self.cooldowns = {}

    @Cog.listener("on_ready")
    async def on_ready_main(self):
        #general
        self.bot.logger.info(f"Bot is ready as {self.bot.user}")
        status = await self.bot.db["status"].find_one({"status": {"$exists": True}})
        await self.bot.change_presence(activity=discord.CustomActivity(name=status["status"] if status else config.bot.default_status))

        #restart
        data = await self.bot.db["restart"].find_one({"restart": "restart"})
        if data:
            channel = self.bot.get_channel(data["channel_id"])
            message = await channel.fetch_message(data["message_id"])
            await message.reply(f"Successfully restarted in `{round(time.time() - data['time'], 1)}` seconds")
            await self.bot.db["restart"].delete_one({"restart": "restart"})

        
    @Cog.listener("on_message")
    async def on_message_afk(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        # Ignore if it's an AFK command
        try:
            prefixes = await self.bot.command_prefix(self.bot, message)
            for prefix in prefixes:
                if message.content.startswith(f"{prefix}afk") or message.content.startswith(f"<@{self.bot.user.id}> afk"):
                    return
        except Exception as e:
            pass

        afk_data = await self.bot.db["afk"].find_one({"uid": message.author.id})
        if afk_data:
            afk_guild = afk_data.get("guild_id", 0)
            if afk_guild == 0 or afk_guild == message.guild.id:
                afk_time = round(time.time() - afk_data["tm"], 0)
                unit = "seconds"

                if afk_time > 86400:
                    afk_time /= 86400
                    unit = "days"
                elif afk_time > 3600:
                    afk_time /= 3600
                    unit = "hours"
                elif afk_time > 60:
                    afk_time /= 60
                    unit = "minutes"

                await message.channel.send(
                    f"{message.author.mention} I have removed your AFK. You were AFK for {int(round(afk_time))} {unit}."
                )
                await self.bot.db["afk"].delete_one({"uid": message.author.id})

        if message.mentions:
            for user in message.mentions:
                user_afk = await self.bot.db["afk"].find_one({"uid": user.id})
                if user_afk:
                    afk_guild = user_afk.get("guild_id", 0)
                    if afk_guild == 0 or afk_guild == message.guild.id:
                        reason = user_afk.get("reason", " ")
                        tm = int(user_afk.get("tm", time.time()))

                        embed = discord.Embed(
                            title=f"{user.display_name} is AFK since <t:{tm}:R>",
                            color=config.color.no_color
                        )

                        if reason.strip():
                            embed.description = f"{config.emoji.arrow} **Reason:** {reason[:2500]}"

                        await message.reply(embed=embed)

    # events for autoresponder
    @Cog.listener("on_message")
    @commands.guild_only()
    async def on_message_autoresponder(self, message: discord.Message):

        if message.author.bot or not message.guild:\
            return
        guild_id = message.guild.id

        # Get autoresponder data for this guild
        responses = self.bot.autoresponder_cache.get(guild_id, [])
        
        if responses:
            # Check exact matches first
            message_content = message.content.lower()
            
            # Check exact matches
            for resp in responses:
                if resp["matchmode"] == "exact" and message_content == resp["trigger"]:
                    await message.reply(resp["responce"])
                    return
            
            # Check includes matches
            for resp in responses:
                if resp["matchmode"] == "includes" and resp["trigger"] in message_content:
                    await message.reply(resp["responce"])
                    return
    
    @commands.Cog.listener("on_message")
    @commands.guild_only()
    async def on_message_level(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        # Optional cooldown to prevent spam leveling
        key = (message.guild.id, message.author.id)
        if key in self.cooldowns:
            if asyncio.get_event_loop().time() - self.cooldowns[key] < config.level.cooldown:  #cooldown
                return
        self.cooldowns[key] = asyncio.get_event_loop().time()

        # Check if level system is enabled
        data = await self.bot.db["level_config"].find_one({"guild_id": message.guild.id})
        if not data or not data.get("enabled", False):
            return

        base_xp = config.level.base_xp
        growth_rate = config.level.growth_rate
        xp_per_message = config.level.xp_per_message

        # Get user's current data
        user_data = await self.bot.db["level_data"].find_one({
            "guild_id": message.guild.id,
            "user_id": message.author.id
        }) or {"total_xp": 0, "weekly_xp": 0, "level": 1}

        previous_level = user_data.get("level", 1)
        total_xp = user_data.get("total_xp", 0) + xp_per_message

        # Calculate level from total_xp
        level = 1
        xp_needed = base_xp
        accumulated_xp = 0

        while total_xp >= accumulated_xp + xp_needed:
            accumulated_xp += xp_needed
            level += 1
            xp_needed = int(base_xp * (growth_rate ** (level - 1)))

        # Update DB with both total and weekly XP
        await self.bot.db["level_data"].update_one(
            {"guild_id": message.guild.id, "user_id": message.author.id},
            {
                "$set": {"level": level},
                "$inc": {"total_xp": xp_per_message, "weekly_xp": xp_per_message}
            },
            upsert=True
        )

        # Send level-up message if level changed
        if level > previous_level:
            # add auto role 
            role_data = await self.bot.db["level_autorole"].find_one({
                "guild_id": message.guild.id,
                "level": level
            })
            assigned = False
            if role_data:
                role = message.guild.get_role(role_data["role_id"])
                if role:
                    try:
                        await message.author.add_roles(role)
                        assigned = True
                    except discord.Forbidden:
                        pass
                        
            channel = data.get("channel_id")

            if channel:
                channel = self.bot.get_channel(channel)

                if not channel:
                    channel = message.channel
            else:
                channel = message.channel

            embed = discord.Embed()
            embed.title=f"{message.author.display_name} leveled up!"
            embed.color=discord.Colour.magenta()
            embed.set_thumbnail(url=message.author.avatar.url)
            if message.guild.icon:
                embed.set_footer(text=message.guild.name, icon_url=message.guild.icon.url)
            else:
                embed.set_footer(text=message.guild.name)

            if assigned:
                embed.description=f"**Congratulations**\nyou are now level **{level}!**\n> **Role Added:** {role.mention}"
            else:
                embed.description=f"**Congratulations**\nyou are now level **{level}!**"
            
            
            await channel.send(content=message.author.mention, embed=embed)

    # event for bot ping
    @Cog.listener("on_message")
    async def on_message_bot_ping(self, message: discord.Message):
        if message.author.bot:
            return
        if message.content != f"<@{self.bot.user.id}>":
            return
        
        embed = discord.Embed(color=discord.Colour.green())
        embed.set_author(name=message.guild.name, icon_url=message.guild.icon.url if message.guild.icon else None)
        embed.set_thumbnail(url=message.author.avatar.url if message.author.avatar else None)
        embed.description = ""
        embed.description += f"{config.emoji.pp_cringe} **Hello** {message.author.mention}\n"
        embed.description += f"{config.emoji.dot} **Prefix:** `{self.bot.prefix_cache.get(message.guild.id, config.bot.default_prefix)}`\n"
        embed.description += f"\n{config.emoji.dot} **Use** `{self.bot.prefix_cache.get(message.guild.id, config.bot.default_prefix)}help` for more info "
        embed.set_footer(text="Made with ❤️ by Mainak")
        await message.reply(embed=embed)

    # deleting data when bot leaves a guild
    @Cog.listener("on_guild_remove")
    async def on_guild_remove_autoresponder(self, guild: discord.Guild):

        await self.bot.db["autoresponder"].delete_one({
            "guild_id" : guild.id
        })
        self.bot.autoresponder_cache.pop(guild.id, None)


            
    #guild join logs
    @Cog.listener()
    async def on_guild_join(self, guild : discord.Guild):

        embed = discord.Embed()
        embed.title = guild.name
        embed.description = f"**ID:** {guild.id}\n**Name:** {guild.name}\n **Owner:** [`{guild.owner.name}`] [`{guild.owner.id}`]\n **Members:** `{guild.member_count}`"
        embed.color = discord.Colour.green()
        try:
            embed.set_thumbnail(url=guild.icon.url)
        except:
            pass

        channel = self.bot.get_channel(config.loging_channels.join)

        await channel.send(embed=embed)
        count_channel = self.bot.get_channel(config.loging_channels.count)
        await count_channel.send(f"# {len(self.bot.guilds)}")


    #guild leave logs
    @Cog.listener("on_guild_remove")
    async def on_guild_remove_logging(self, guild : discord.Guild):

        embed = discord.Embed()
        embed.title = guild.name
        embed.description = f"**Name:** {guild.name}\n **Owner:** [`{guild.owner.name}`] [`{guild.owner.id}`]\n **Members:** `{guild.member_count}`"
        embed.color = discord.Colour.green()
        try:
            embed.set_thumbnail(url=guild.icon.url)
        except:
            pass

        channel = self.bot.get_channel(config.loging_channels.leave)

        await channel.send(embed=embed)
        count_channel = self.bot.get_channel(config.loging_channels.count)
        await count_channel.send(f"# {len(self.bot.guilds)}")