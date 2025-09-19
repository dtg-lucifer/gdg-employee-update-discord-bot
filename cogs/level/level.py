import discord
from discord.ext import commands, tasks
from core.cog import Cog, MyBot
import config
from PIL import Image, ImageDraw, ImageFont
import io
import os
import random
import datetime
import time

class Level(Cog):
    def __init__(self, bot: MyBot):
        self.bot = bot
        self.emoji = config.emoji.cog_level
        self.reset_weekly_xp.start()

    @tasks.loop(minutes=1)
    async def reset_weekly_xp(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        if now.weekday() == 6 and now.hour == 0 and now.minute == 0:  # Sunday 00:00 UTC
            await self.bot.db["level_data"].update_many({}, {"$set": {"weekly_xp": 0}})
            loging_channel = self.bot.get_channel(config.loging_channels.bot_log)
            try:
                embed = discord.Embed(
                    description="> **Weekly XP has been reset**",
                    color=discord.Color.green(),
                )
                await loging_channel.send(embed=embed)
            except Exception as e:
                print(f"Error sending weekly XP reset log: {e}")
 
 
    @reset_weekly_xp.before_loop
    async def before_reset_weekly_xp(self):
        await self.bot.wait_until_ready()


    @commands.hybrid_group(
        name="levelup",
        description="Level commands",
        invoke_without_command=True,
    )

    async def levelup(self, ctx: commands.Context):
        """Level commands"""
        await ctx.send_help(ctx.command)
    

    @levelup.group(name="role", description="Levelup role commands")
    async def levelup_role(self, ctx: commands.Context):
        """Levelup role commands"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)
            return
        await ctx.send_help(ctx.command)

    @levelup_role.command(name="add", description="Add a role to level up")
    @commands.has_permissions(administrator=True)
    async def add_role(self, ctx: commands.Context, level: int, role: discord.Role):
        """Add a role to level up"""
        if level < 1:
            await ctx.send("❌ Level must be ≥ 1.")
            return

        if role.is_bot_managed():
            await ctx.send("❌ I cannot assign this role, it is used by a bot.")
            return
        if role.is_default():
            await ctx.send("❌ I cannot assign this role. it is a default role")
            return
        if role.is_premium_subscriber():
            await ctx.send("❌ I cannot assign this role, it is a server boost role.")
            return
        if role.position >= ctx.guild.me.top_role.position:
            await ctx.send("❌ I cannot assign this role, it is higher than my highest role.")
            return
        if role.position >= ctx.author.top_role.position:
            await ctx.send("❌ I cannot assign this role, it is higher than your highest role.")
            return

        await self.bot.db["level_autorole"].update_one(
            {"guild_id": ctx.guild.id, "level": level},
            {"$set": {"role_id": role.id}},
            upsert=True,
        )
        embed = discord.Embed(
            description=f"> **Role {role.name} added for level {level}**",
            color=discord.Color.green(),
        )
        await ctx.send(embed=embed)

    @levelup_role.command(name="remove", description="Remove a role from level up")
    @commands.has_permissions(administrator=True)
    async def remove_role(self, ctx: commands.Context, level: int):
        """Remove a role from level up"""
        data = await self.bot.db["level_autorole"].find_one(
            {"guild_id": ctx.guild.id, "level": level}
        )
        if not data:
            embed = discord.Embed(
                description="> **No levelup role found**",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)
            return
        await self.bot.db["level_autorole"].delete_one(
            {"guild_id": ctx.guild.id, "level": level}
        )
        embed = discord.Embed(
            description=f"> **Role removed for level {level}**",
            color=discord.Color.red(),
        )
        await ctx.send(embed=embed)

    @levelup_role.command(name="list", description="List all levelup roles")
    async def list_roles(self, ctx: commands.Context):
        """List all levelup roles"""
        data = await self.bot.db["level_autorole"].find({"guild_id": ctx.guild.id}).to_list()
        if not data:
            embed = discord.Embed(
                description="> **No levelup roles found**",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(
            title=f"{ctx.guild.name} Levelup Roles",
            color=discord.Color.blue(),
        )
        embed.set_author(
            name=f"Levelup Roles",
        )
        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)

        embed_text = []
        for entry in data:
            role = ctx.guild.get_role(entry["role_id"])
            if role:
                embed_text.append(f"**Level:** `{entry['level']}` {config.emoji.arrow} {role.mention}\n")

        embed.description = "\n".join(embed_text)
        await ctx.send(embed=embed)

    @levelup_role.command(name="sync", description="Sync levelup roles")
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 300, commands.BucketType.guild)
    async def sync_roles(self, ctx: commands.Context):
        """Sync levelup roles"""
        data = await self.bot.db["level_autorole"].find({"guild_id": ctx.guild.id}).to_list()
        if not data:
            embed = discord.Embed(
                description="> **No levelup roles found**",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)
            return
        
        msg: discord.Message = await ctx.send("Syncing levelup roles...")

        for entry in data:
            role = ctx.guild.get_role(entry["role_id"])
            level = entry["level"]
            if role:
                filename = f"tempFiles/{ctx.guild.id}sync_logs.txt"
                with open(filename, "w") as f:
                    for member in ctx.guild.members:
                        if member.bot:
                            continue
                        data = await self.bot.db["level_data"].find_one(
                            {"guild_id": ctx.guild.id, "user_id": member.id}
                        )
                        if data and data["level"] >= level:
                            if role not in member.roles:
                                try:
                                    await member.add_roles(role, reason="Levelup role")
                                    f.write(f"Added {role.name} to {member.name}\n")
                                except:
                                    f.write(f"Failed to add {role.name} to {member.name}\n")
                        elif data and data["level"] < level:
                            if role in member.roles:
                                try:
                                    await member.remove_roles(role, reason="Levelup role")
                                    f.write(f"Removed {role.name} from {member.name}\n")
                                except:
                                    f.write(f"Failed to remove {role.name} from {member.name}\n")
                        time.sleep(0.1)

        await msg.delete()
        embed = discord.Embed(
            description="> **Levelup roles synced**",
            color=discord.Color.green(),
        )
        await ctx.send(embed=embed, file=discord.File(fp=filename, filename="sync_logs.txt"))
        os.remove(filename)

    @levelup.command(name="enable", description="Enable level-up announcement")
    @commands.has_permissions(administrator=True)
    async def enable_announce(self, ctx: commands.Context):
        """Enable level announcement"""
        await self.bot.db["level_config"].update_one(
            {"guild_id": ctx.guild.id},
            {"$set": {"enabled": True}},
            upsert=True,
        )
        embed = discord.Embed(
            description="> **Level announcement enabled**",
            color=discord.Color.green(),
        )
        await ctx.send(embed=embed)

    @levelup.command(name="disable", description="Disable level-up announcement")
    @commands.has_permissions(administrator=True)
    async def disable_announce(self, ctx: commands.Context):
        """Disable level announcement"""
        await self.bot.db["level_config"].update_one(
            {"guild_id": ctx.guild.id},
            {"$set": {"enabled": False}},
            upsert=True,
        )
        embed = discord.Embed(
            description="> **Level announcement disabled**",
            color=discord.Color.red(),
        )
        await ctx.send(embed=embed)
    
    @levelup.command(name="set", description="Set the level announcement channel")
    @commands.has_permissions(administrator=True)
    async def set_announce(self, ctx: commands.Context, channel: discord.TextChannel):
        """Set the announcement channel"""
        await self.bot.db["level_config"].update_one(
            {"guild_id": ctx.guild.id},
            {"$set": {"channel_id": channel.id}},
            upsert=True,
        )
        embed = discord.Embed(
            description=f"> **Level announcement channel set to {channel.mention}**",
            color=discord.Color.green(),
        )
        await ctx.send(embed=embed)

    @commands.command(name="level", description="Check your level")
    async def level(self, ctx: commands.Context, member: discord.Member = None):
        """Check your level or someone else's level"""
        if member is None:
            member = ctx.author

        data = await self.bot.db["level_data"].find_one(
            {"guild_id": ctx.guild.id, "user_id": member.id}
        )
        rank = await self.bot.db["level_data"].find_one(
            {"guild_id": ctx.guild.id, "user_id": member.id}
        )

        if rank is None:
            rank = 0
        else:
            rank = await self.bot.db["level_data"].count_documents(
                {"guild_id": ctx.guild.id, "total_xp": {"$gt": rank["total_xp"]}}
            ) + 1

        if data is None:
            embed = discord.Embed(
                description=f"> **{member.name}** has not leveled up yet.",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)
            return
        
        weekly_xp = data.get("weekly_xp", 0)
        if weekly_xp is None:
            weekly_xp = 0

        weekly_rank = await self.bot.db["level_data"].count_documents(
            {"guild_id": ctx.guild.id, "weekly_xp": {"$gt": weekly_xp}}
        ) + 1
        if weekly_rank is None:
            weekly_rank = "N/A"
        
        level = data.get("level", 1)
        total_xp = data.get("total_xp", 0)

        base_xp = 10
        growth_rate = 1.2

        total_xp_for_next_level = 0
        for i in range(1, level + 1):  # level + 1 means "up to next level"
            total_xp_for_next_level += int(base_xp * (growth_rate ** (i - 1)))

        template = Image.open("files/rank.png").convert("RGBA")

        s = 165  # Size of the avatar
        avatar_bytes = io.BytesIO(await member.display_avatar.read())
        avatar = Image.open(avatar_bytes).resize((s, s)).convert("RGBA")
        mask = Image.new("L", (s, s), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0, s, s), fill=255)

        avatar_x, avatar_y = 92, 75
        template.paste(avatar, (avatar_x, avatar_y), mask)

        draw = ImageDraw.Draw(template)

        font_path_bold = "files/Cat Song.ttf"

        font_username = ImageFont.truetype(font_path_bold, 40)
        font_value = ImageFont.truetype(font_path_bold, 35)

        draw.text((300, 70), member.display_name, font=font_username, fill="#f78d1f")
        draw.text((355, 210), f"#{rank}", font=font_value, fill="#f78d1f")
        draw.text((510, 210), f"#{weekly_rank}", font=font_value, fill="#ffffff")
        draw.text((675, 210), str(weekly_xp), font=font_value, fill="#ffffff")
        draw.text((1072, 80), str(level), font=font_value, fill="#f78d1f")
        draw.text((1040, 230), f"{total_xp}/{total_xp_for_next_level}", font=font_value, fill="#ffffff")

        filename = f"rank_card_{member.id}{ctx.guild.id}{random.randrange(1000,9999)}.png"
        template.save(f"tempFiles/{filename}")
        await ctx.send(file=discord.File(fp=f"tempFiles/{filename}", filename="homie_rank_card.png"))
        os.remove(f"tempFiles/{filename}")  # Clean up the file after sending


    @commands.command(name="givelevel", description="Give a user a specific level")
    @commands.has_permissions(administrator=True)
    async def givelevel(self, ctx: commands.Context, member: discord.Member, level: int):
        """Assign a specific level to a user, and calculate the XP automatically."""
        if level < 1:
            await ctx.send("❌ Level must be ≥ 1.")
            return

        base_xp = config.level.base_xp
        growth_rate = config.level.growth_rate

        # Calculate total XP required to reach the given level
        total_xp = 0
        for i in range(1, level):
            total_xp += int(base_xp * (growth_rate ** (i - 1)))

        # Update the user's level and XP
        await self.bot.db["level_data"].update_one(
            {"guild_id": ctx.guild.id, "user_id": member.id},
            {"$set": {"level": level, "total_xp": total_xp}},
            upsert=True
        )

        await ctx.send(f"✅ Set {member.mention} to level **{level}** with **{total_xp} XP**.")

    @commands.command(name="leaderboard", aliases=["lb"], description="Show the level leaderboard")
    async def leaderboard(self, ctx: commands.Context):
        """Show the level leaderboard"""
        data = await self.bot.db["level_data"].find({"guild_id": ctx.guild.id}).sort("total_xp", -1).to_list()

        if not data:
            embed = discord.Embed(
                description="> **No levels found**",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(
            title=ctx.guild.name,
            color=discord.Color.blue(),
        )
        embed.set_author(
            name=f"Level Leaderboard",
        )

        embed_text = []
        for i, entry in enumerate(data, start=1):
            if i > 10:
                break
            if i == 1:
                i = "🥇"
            elif i == 2:
                i = "🥈"
            elif i == 3:
                i = "🥉"
            else:
                i = f"#{i}"

            member = ctx.guild.get_member(entry["user_id"])
            if member:
                embed_text.append(f"{i} {config.emoji.arrow} {member.mention}")
                embed_text.append(f"{config.emoji.space}Level: `{entry['level']}`")
                embed_text.append(f"{config.emoji.space}XP: `{entry['total_xp']}`\n")

        embed.description = "\n".join(embed_text)
        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)

        list_btn = discord.ui.Button(
            label="Full Leaderboard",
            style=discord.ButtonStyle.blurple,
        )
        view = discord.ui.View(timeout=None)
        view.add_item(list_btn)

        async def list_btn_callback(interaction: discord.Interaction):
            await interaction.response.defer()
            filename = f"tempFiles/{ctx.guild.id}_leaderboard.txt"
            with open(filename, "w") as f:
                content = []
                for i, entry in enumerate(data, start=1):
                    member = ctx.guild.get_member(entry["user_id"])
                    if member:
                        content.append(f"{i}. {member.name}#{member.discriminator} - Level: {entry['level']} - XP: {entry['total_xp']}")
                
                f.write("\n\n".join(content))
            
            await interaction.followup.send(
                file=discord.File(fp=filename, filename="leaderboard.txt"),
                ephemeral=True,
            )
            os.remove(filename)

        list_btn.callback = list_btn_callback
        await ctx.send(embed=embed, view=view)

    @commands.command(name="weeklyleaderboard", aliases=["lbw"], description="Show the weekly level leaderboard")
    async def weekly_leaderboard(self, ctx: commands.Context):
        """Show the weekly level leaderboard"""
        data = await self.bot.db["level_data"].find({"guild_id": ctx.guild.id}).sort("weekly_xp", -1).to_list()

        if not data:
            embed = discord.Embed(
                description="> **No levels found**",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)
            return
        embed = discord.Embed(
            title=ctx.guild.name,
            color=discord.Color.blue(),
        )
        embed.set_author(
            name=f"Weekly Level Leaderboard",
        )
        embed_text = []
        for i, entry in enumerate(data, start=1):
            if i > 10:
                break
            if i == 1:
                i = "🥇"
            elif i == 2:
                i = "🥈"
            elif i == 3:
                i = "🥉"
            else:
                i = f"#{i}"

            member = ctx.guild.get_member(entry["user_id"])
            if member:
                embed_text.append(f"{i} {config.emoji.arrow} {member.mention}")
                embed_text.append(f"{config.emoji.space}Level: `{entry['level']}`")
                embed_text.append(f"{config.emoji.space}Weekly XP: `{entry['weekly_xp']}`\n")
        embed.description = "\n".join(embed_text)
        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)
        list_btn = discord.ui.Button(
            label="Full Leaderboard",
            style=discord.ButtonStyle.blurple,
        )
        view = discord.ui.View(timeout=None)
        view.add_item(list_btn)
        async def list_btn_callback(interaction: discord.Interaction):
            await interaction.response.defer()
            filename = f"tempFiles/{ctx.guild.id}_weekly_leaderboard.txt"
            with open(filename, "w") as f:
                content = []
                for i, entry in enumerate(data, start=1):
                    member = ctx.guild.get_member(entry["user_id"])
                    if member:
                        content.append(f"{i}. {member.name}#{member.discriminator} - Level: {entry['level']} - Weekly XP: {entry['weekly_xp']}")
                
                f.write("\n\n".join(content))
            
            await interaction.followup.send(
                file=discord.File(fp=filename, filename="weekly_leaderboard.txt"),
                ephemeral=True,
            )
            os.remove(filename)
        list_btn.callback = list_btn_callback
        await ctx.send(embed=embed, view=view)


