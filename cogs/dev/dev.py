import discord
from discord.ext import commands
from core.cog import Cog
from core.bot import MyBot
import config
import time
import psutil
import speedtest
import subprocess
from discord.ui import View, Button
import random
import string
from typing import Optional


class Dev(Cog):
    def __init__(self, bot: MyBot):
        self.bot = bot

    def generate_token_code(self, length=12):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

    #dev command for command sync
    @commands.command(hidden=True)
    @commands.is_owner()
    async def sync(self, ctx:commands.Context):
        
        await self.bot.tree.sync()
        await ctx.send("Synced Globally")
        
    
    #dev command for stats
    @commands.command(hidden=True)
    @commands.is_owner()
    async def stats(self, ctx:commands.Context):
        
        #stats
        total_memory = psutil.virtual_memory().total >> 20
        used_memory = psutil.virtual_memory().used >> 20
        cpu_used = str(psutil.cpu_percent())
        total_members = sum(i.member_count for i in self.bot.guilds)
        cached_members = len(self.bot.users)
        
        
        #embed properties
        embed = discord.Embed(description=None)
        embed.title = F"**__{self.bot.user.display_name}__**"
        embed.colour = discord.Color.red()
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        
        
        arrow=config.emoji.arrow
        
        guild_value = len(self.bot.guilds)
        embed.add_field(name="Servers", value=f"**[Total** {arrow} {guild_value}**]**")
        embed.add_field(name="Members", value=f"**[Total** {arrow} {total_members}**]** \n **[Cached** {arrow} {cached_members}**]** ")
        embed.add_field(
            name="Stats",
            value=f"**[Ping** {arrow} {round(self.bot.latency * 1000, 2)}ms]",
        )
        embed.add_field(name="System", value=f"**[RAM** {arrow} {used_memory} / {total_memory} MB**]** \n **[CPU used** {arrow} {cpu_used}%**]**"),
        embed.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar.url)        
        await ctx.send(embed=embed) 
        
    

    @commands.command()
    @commands.is_owner()
    async def invite(self, ctx: commands.Context, guild_id: int):

        try:
            guild = self.bot.get_guild(guild_id)

            invite = await guild.text_channels[0].create_invite(max_uses=1)
            
            await ctx.send(invite)
            
        except Exception as e:
            await ctx.send(e)



    @commands.command(aliases = ["nplist"])
    @commands.is_owner()
    async def np_list(self, ctx: commands.Context):

        np_list = await self.bot.db["np"].find({}).to_list()
 
        users = []
        n = 1
        for uid in np_list:
            try:
                user = self.bot.get_user(uid['uid'])
                users.append(f"{n}. {user.mention}")
            except:
                users.append(f"{n}. `{uid['uid']}`")

            n = n+1

        embed = discord.Embed()
        embed.color=config.color.no_color
        embed.description = "\n".join(users)

        await ctx.send(embed=embed)


    @commands.command(name="vps_speed")
    @commands.is_owner()
    async def vps_speed(self, ctx: commands.Context):

        embed = discord.Embed(color=config.color.no_color)
        embed.description = "This can be dangerous because it uses a lot of bandwidth."
        confirm_btn = Button(
            label="Confirm",
            style=discord.ButtonStyle.green
        )
        cancel_btn = Button(
            label="Cancel",
            style=discord.ButtonStyle.red
        )
        view = View(timeout=None)
        view.add_item(confirm_btn)
        view.add_item(cancel_btn)

        msg = await ctx.send(embed=embed, view=view)

        async def confirm_callback(interaction: discord.Interaction):
            await interaction.response.defer()
            if interaction.user.id != ctx.author.id:
                return await interaction.response.send_message("You can't use this button.", ephemeral=True)
            await msg.delete()

            embed.description = "⌛ Please wait...."

            msg2: discord.Message = await ctx.send(embed=embed)
            test = speedtest.Speedtest()

            download = test.download()
            upload = test.upload()

            download = round(download / 10**6, 1)
            upload = round(upload / 10**6, 1)

            if download >= 1024:
                dl_speed = f"{(download / 1024)} GBPS"
            else:
                dl_speed = f"{download} MBPS"

            if upload >= 1024:
                ul_speed = f"{(upload / 1024)} GBPS"
            else:
                ul_speed = f"{upload} MBPS"

            new_embed = discord.Embed(color=config.color.no_color)
            new_embed.description = f"> **Download:** {dl_speed}\n> **Upload:** {ul_speed}"

            await msg2.edit(embed=new_embed)

        async def cancel_callback(interaction: discord.Interaction):
            await interaction.response.defer()
            if interaction.user.id != ctx.author.id:
                return await interaction.response.send_message("You can't use this button.", ephemeral=True)
            await msg.delete()

        confirm_btn.callback = confirm_callback
        cancel_btn.callback = cancel_callback

    @commands.command()
    @commands.is_owner()
    async def restart(self, ctx: commands.Context):

        # get all active voice clients
        voice_clients = [vc for vc in self.bot.voice_clients]
        voice_clients = len(voice_clients)
        continue_btn = Button(
            label="Continue",
            style=discord.ButtonStyle.green
        )
        view = View(timeout=None)
        view.add_item(continue_btn)
        
        await ctx.send(f"> Are you sure?", view=view)
        async def btn_callback(interaction: discord.Interaction):
            await interaction.response.defer()
            if interaction.user.id != ctx.author.id:
                return await interaction.response.send_message("You can't use this button.", ephemeral=True)

        
            await ctx.send("Restarting the bot using `pm2 restart homie`...")
            await self.bot.db["restart"].insert_one({
                "restart": "restart",
                "time": time.time(),
                "channel_id": ctx.channel.id,
                "message_id" : ctx.message.id
            })

            try:
                subprocess.run(["pm2", "restart", "homie"], capture_output=True, text=True)
            except Exception as e:
                await ctx.send(f"❌ Exception occurred: `{str(e)}`")

        continue_btn.callback = btn_callback

    @commands.command()
    @commands.is_owner()
    async def gitpull(self, ctx: commands.Context):
        try:
            subprocess.run(["git", "pull"], capture_output=True, text=True)
            await ctx.send("Successfully pulled the latest changes from the repository.")
        except Exception as e:
            await ctx.send(f"❌ Exception occurred: `{str(e)}`")


        
    @commands.command(name="guildlist")
    @commands.is_owner()
    async def guildlist(self, ctx: commands.Context, rev: Optional[str]):
        """
        List all guilds the bot is in with pagination.
        """

        if rev:
            reverse = False
        else:
            reverse = True

        guilds = sorted(self.bot.guilds, key=lambda g: g.member_count, reverse=reverse)
        
        pages = []
        for i in range(0, len(guilds), 10):
            page_guilds = guilds[i:i+10]
            guild_info = [f"{i+j+1}. **{g.name}** | **ID:** `{g.id}` | **Members:** `{g.member_count}`\n" for j, g in enumerate(page_guilds)]
            embed = discord.Embed(
                title=f"Guild List (Page {len(pages)+1}/{(len(guilds)-1)//10+1})",
                description="\n".join(guild_info),
                color=discord.Color.blue()
            )
            embed.set_footer(text=f"Total Guilds: {len(guilds)} | Total Users: {sum(g.member_count for g in guilds)}")
            pages.append(embed)
        
        if not pages:
            return await ctx.send("No guilds found.")
        
        class PaginatorView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=60)
                self.current_page = 0
            
            @discord.ui.button(label="◀️", style=discord.ButtonStyle.gray)
            async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user.id != ctx.author.id:
                    return await interaction.response.send_message("You can't use this button.", ephemeral=True)
                
                self.current_page = max(0, self.current_page - 1)
                await interaction.response.edit_message(embed=pages[self.current_page])
            
            @discord.ui.button(label="▶️", style=discord.ButtonStyle.gray)
            async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user.id != ctx.author.id:
                    return await interaction.response.send_message("You can't use this button.", ephemeral=True)
                
                self.current_page = min(len(pages) - 1, self.current_page + 1)
                await interaction.response.edit_message(embed=pages[self.current_page])
        
        view = PaginatorView()
        await ctx.send(embed=pages[0], view=view)

    @commands.command(name="gleave")
    @commands.is_owner()
    async def gleave(self, ctx: commands.Context, gid: int):
        """
        Make the bot leave a specific guild.
        """
        guild = self.bot.get_guild(gid)
        if not guild:
            return await ctx.send("Guild not found.")

        await guild.leave()
        await ctx.send(f"Left the guild: {guild.name}")

    
    @commands.command(name="setstatus")
    @commands.is_owner()
    async def setstatus(self, ctx: commands.Context, *, status: str):
        """
        Set the bot's status.
        """
        await self.bot.change_presence(activity=discord.CustomActivity(name=status))
        await ctx.send(f"Status set to: {status}")
        await self.bot.db["status"].update_one(
            {},
            {"$set": {"status": status}},
            upsert=True
        )
        await ctx.send("Status saved to the database.")