import discord
from discord.ext import commands
from discord import app_commands
import config
from core.cog import Cog
import random
from main import MyBot
from typing import Optional
import requests
import aiohttp
import wavelink
import time


class Tools (Cog):
    def __init__(self, bot: MyBot):
        self.bot=bot
        self.emoji = config.emoji.cog_tools


    #hybrid command for ping
    @commands.hybrid_command(with_app_command=True, name="ping",description="Shows the latency", aliases=["latency"])
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.user)
    async def ping(self, ctx:commands.Context):

        # bot ping
        bot_ping = int(self.bot.latency*1000)

        # database ping
        tm = time.time()
        await self.bot.db["homie"]["ping"].find_one({"ping":"pong"})
        db_ping = int((time.time()-tm)*1000)

        #cache ping
        tm = time.time()
        self.bot.ping_cache.get("ping")
        cache_ping = round((time.time()-tm)*1000, 3)

        embed = discord.Embed()
        embed.description = f"{config.emoji.bot_ping} Bot ping: `{bot_ping} ms`\n \n{config.emoji.db_ping} Database ping: `{db_ping} ms`\n \n{config.emoji.cache} Cache ping: `{cache_ping} ms`"
        embed.color=config.color.no_color
        
        embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar.url)
        await ctx.send(embed=embed)


    #hybrid command for toss
    @commands.hybrid_command(with_app_command=True,name="toss", description="Toss for head or tail") 
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.user)
    async def toss(self, ctx: commands.Context) :
   
        tossNumber = random.randrange(1,3)
        if (tossNumber == 1) :
            tossResult = "Head"
        else :
            tossResult = "Tail"

        tossResult= "The result is: " + tossResult
        await ctx.send(tossResult)


    #hybrid command for Dice
    @commands.hybrid_command (with_app_command=True, name="dice", description="Roll a dice")
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.user)
    async def dice(self, ctx: commands.Context) :

        diceNumber = random.randrange (1,7)
        await ctx.send(f"You got: {diceNumber}")


    #hybrid command for avatar          
    @commands.hybrid_command(with_app_command=True, name="avatar", description="Get the avatar of a user", aliases=["av", "pfp", "dp", "logo"])
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.user) 
    async def avatar(self, ctx:commands.Context, user: Optional[discord.User]):

        if not user : user=ctx.author

        button = discord.ui.Button(label="Download", emoji="⬇", url = user.avatar.url)
        view = discord.ui.View().add_item(button)

        try:
            avatarEmbed= discord.Embed(title=user.name, color=config.color.no_color)
            avatarEmbed.set_image(url=user.avatar.url)
            await ctx.send(embed=avatarEmbed, view=view)
        except Exception as e:
            await ctx.send(e)



    #hybrid command for calculator
    @commands.hybrid_command(with_app_command=True, name="calculator", description="Solves a numerical problem")
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.user)
    async def calculator(self, ctx: commands.Context, expression: str ):

        embed = discord.Embed()
        embed.color = config.color.no_color
        embed.title = expression

        try:
            embed.description = f"**{eval(expression)}**"
        except:
            embed.description = "Invalid expression"
        
        await ctx.send(embed=embed)
            
                
        
    #hybrid command for get_emoji
    @commands.hybrid_command(name="get_emoji", description="Paste the id of any custom emoji and get the png file")
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.user)
    async def get_emoji(self, ctx:commands.Context,*, emoji_code:str ):
        
        try:
            input= emoji_code.split(":")
            list = []
            for i in input:
                list.append(i)
       
            
            input = str(list[2])
            list=[]
            for char in input :
                if char.isdigit():
                    list.append(char)
                    
                    
            output = int("".join(list))
            
            link = f"https://cdn.discordapp.com/emojis/{output}.png?=1"
            

            try:
                # checking if the link correct or not
                response = requests.head(link)
                response.raise_for_status() 

                button = discord.ui.Button(label="Download", emoji="⬇", url = link)
                view = discord.ui.View().add_item(button)

                embed = discord.Embed()
                embed.set_author(name="Here is you emoji as an image (png format)", icon_url= self.bot.user.avatar.url)
                embed.set_image(url=link)
                embed.set_footer(text= f"Requested by {ctx.author.name}", icon_url= ctx.author.avatar.url)
                await ctx.send(embed=embed, view = view)  

            except:
                await ctx.send("**Given code is wrong**")               

        except Exception as e:
            await ctx.send(e)
            

            
    # slash command for voice move
    @app_commands.command(name="voice_move", description="Move all members from one VC to another")
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.user)
    @commands.has_permissions(move_members = True)
    async def voice_move(self, interaction: discord.Interaction , channel_1: discord.VoiceChannel, channel_2: discord.VoiceChannel ):
        
        await interaction.response.defer(thinking= True)
        
        try:
            members = channel_1.members
        except:
            return await interaction.followup.send(f"No members in {channel_1.name}")
            
        try:
            for member in members:
                
                await member.move_to(channel=channel_2)

            await interaction.followup.send(f"Moved all members from **{channel_1.name}** to **{channel_2.name}**")
        except:
            await interaction.followup.send("I don't have permissions to move the member")
    

    # hybrid command for steal    
    @commands.hybrid_command(name="steal", description="Steals an emoji from another server")
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.user)
    @commands.has_permissions(manage_emojis=True)
    async def steal(self, ctx:commands.Context, emote:str, name: str = None):
        if name is None:
            name = "Stolen_emoji"
        try:
            if emote[0] == '<':
                emoji_name = emote.split(':')[2][:-1]
                anim = emote.split(':')[0]
                if anim == '<a':
                    url = f'https://cdn.discordapp.com/emojis/{emoji_name}.gif'
                else:
                    url = f'https://cdn.discordapp.com/emojis/{emoji_name}.png'
                try:
                    response = requests.get(url)
                    img = response.content
                    emote = await ctx.guild.create_custom_emoji(name=name,
                                                                image=img)
                    return await ctx.send(
                        embed=discord.Embed(description=f"added {emote} successfully",
                                            color=config.color.no_color))
                except Exception:
                    return await ctx.send(
                        embed=discord.Embed(description=f"failed to add emoji",
                                            color=config.color.no_color))
            else:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(emote) as resp:
                            if resp.status != 200:
                                return await ctx.send("Failed to fetch image from URL. Please ensure the URL is valid.")

                            image_data = await resp.read()
                except aiohttp.ClientError:
                    return await ctx.send("Failed to fetch image from URL. Please ensure the URL is accessible.")

                try:
                    emoji = await ctx.guild.create_custom_emoji(name=name, image=image_data)
                    await ctx.send(f"Emoji {emoji} added successfully!")
                except discord.HTTPException as e:
                    await ctx.send(f"Failed to add emoji: {e}")
        except Exception as e:
            return await ctx.send(
                embed=discord.Embed(description=f"Failed to add emoji: {e}",
                                    color=0x2f3136))       
            

    # slash command for weather    
    @commands.command(name = "weather", description = "Shows the weather details of a given location")
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.user)
    async def weather(self, ctx: commands.Context, *, city: str):  
        

        base_url = "http://api.openweathermap.org/data/2.5/weather?"
            
        complete_url = base_url + "appid=" + config.api.weather + "&q=" + city
        data = requests.get(complete_url).json()

        
        
        if data["cod"] != "404":
            async with ctx.typing():
                
                
                main = data["main"]
                current_temperature = main["temp"]
                current_temperature_celsiuis = str(round(current_temperature - 273.15))
                current_pressure = main["pressure"]
                current_humidity = main["humidity"]
                weather = data["weather"]
                weather_description = weather[0]["description"]      
            
        
                weather_description = weather[0]["description"]
                embed = discord.Embed(title=f"**Weather in {city.capitalize()}**",
                                color= config.color.no_color,
                                timestamp=ctx.message.created_at,)
                
                embed.add_field(name="**Descripition**", value=f"**{str(weather_description).capitalize()}**", inline=False)
                embed.add_field(name="**Temperature(C)**", value=f"**{current_temperature_celsiuis}°C**", inline=False)
                embed.add_field(name="**Humidity(%)**", value=f"**{current_humidity}%**", inline=False)
                embed.add_field(name="**Atmospheric Pressure **", value=f"**{round((current_pressure/1013.25), 2)} atm ({current_pressure} hPa)**", inline=False)
                
                try:
                    embed.set_thumbnail(url=config.images.weather_thumbnail)
                except:
                    embed.set_thumbnail(url=self.bot.user.avatar.url)
                
                embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
        else:
            await ctx.send("City not found.")



    # hybrid commadn for afk
    @commands.hybrid_command(name ="afk", description = "Set your afk status")
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.user)
    async def afk(self, ctx: commands.Context,* , reason: Optional[str]):

        if not reason: reason = " "

        embed = discord.Embed() 
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.title = "Choose your AFK style:"
        embed.color = config.color.no_color

        server_afk_button = discord.ui.Button(label="Server AFK", style= discord.ButtonStyle.green)
        global_afk_button = discord.ui.Button(label="Global AFK", style= discord.ButtonStyle.green)

        view = discord.ui.View()
        view.add_item(server_afk_button)
        view.add_item(global_afk_button)

        msg = await ctx.send(embed=embed,view=view)

        async def server_callback(interaction: discord.Interaction):

            await interaction.response.defer()

            if ctx.author.id != interaction.user.id:
                return await interaction.followup.send("You can't interact to this", ephemeral=True)
            
            document = {
                "uid" : ctx.author.id,
                "reason" : reason,
                "tm": time.time(),
                "guild_id" : ctx.guild.id
            }

            await self.bot.db["afk"].insert_one(document=document)

            await msg.edit(content=f"{ctx.author.mention} **Your are now afk in this server:** {reason}", embed= None, view=None)

        async def global_callback(interaction: discord.Interaction):

            await interaction.response.defer()
            
            if ctx.author.id != interaction.user.id:
                return await interaction.followup.send("You can't interact to this", ephemeral=True)
            

            document = {
                "uid" : ctx.author.id,
                "reason" : reason,
                "tm": time.time(),
                "guild_id" : 0
            }

            await self.bot.db["afk"].insert_one(document=document)

                
            await msg.edit(content=f"{ctx.author.mention} **Your are now afk globally:** {reason}", embed= None, view=None)


        server_afk_button.callback = server_callback
        global_afk_button.callback = global_callback



    #prefix command for server_icon
    @commands.command(name = "server_icon", description = "Get the icon of the server", aliases =["sav"])
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.user)
    async def server_icon(self, ctx:commands.Context):

        button = discord.ui.Button(label="Download", emoji="⬇", url = ctx.guild.icon.url)
        view = discord.ui.View().add_item(button)

        embed = discord.Embed()
        embed.title = ctx.guild.name
        embed.set_image(url=ctx.guild.icon.url)
        embed.color = config.color.no_color

        await ctx.send(embed=embed, view=view)



    #prefix command for server_info
    @commands.command(name = "server_info", description = "See the icon of the server", aliases =["server"])
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.user)
    async def server_info(self, ctx:commands.Context):


        embed = discord.Embed()
        embed.title = "Server Info"
        embed.set_thumbnail(url=ctx.guild.icon.url)
        embed.color = config.color.no_color

        guild = ctx.guild

        embed.add_field(name="Name:", value = guild.name, inline= False)
        embed.add_field(name="Owner:", value = guild.owner.mention, inline= False)
        embed.add_field(name="Members:", value = guild.member_count, inline= False)
        embed.add_field(name="Created at:", value = f"<t:{int(guild.created_at.timestamp())}:F> (<t:{int(guild.created_at.timestamp())}:R>)", inline= False)
        embed.add_field(name="Server boost:", value = f"{guild.premium_subscription_count} `(Level: {guild.premium_tier})`", inline= False)
        embed.add_field(name="Channel:", value = len(guild.channels), inline = True)
        embed.add_field(name="Roles:", value = len(guild.roles), inline = True)
        embed.add_field(name="Emoji:", value = len(guild.emojis), inline = True)
        embed.add_field(name="Stickers:", value = len(guild.stickers), inline = True)


        embed.set_footer(text=f"Requested by: {ctx.author.name}", icon_url = ctx.author.avatar.url)
        await ctx.send(embed=embed)


    @commands.command(name = "userinfo", description = "Shows information about the user", aliases = ["ui"])
    async def userinfo(self, ctx: commands.Context, user:Optional[discord.Member]):

        if not user:
            user = ctx.author

        embed = discord.Embed(color=config.color.no_color)

        # embed.title = "User Information"
        embed.set_author(icon_url = self.bot.user.avatar.url, name = "User Information")
        embed.set_thumbnail(url=user.avatar.url)

        personal_info = f"**Personal Information**\n> **Display Name: ** {user.display_name}\n> **Username: **{user.name}\n> **ID: ** {user.id}\n> **Joined: **<t:{int(user.created_at.timestamp())}:F> (<t:{int(user.created_at.timestamp())}:R>)\n"
        guild_info = f"**Guild Profile**\n> **Joined at: <t:{int(user.joined_at.timestamp())}:F> (<t:{int(user.joined_at.timestamp())}:R>)**\n"
        roles = ""
        for role in user.roles:
            if str(role.name) != "@everyone" and str(role.name) != "@here":
                roles = roles + " " + role.mention
        
        activities = ""

        for activity in user.activities:
            activities = activities + " " + activity.name

        roles = f"**Roles**\n> **Top Role: **{user.top_role.mention}\n> **Roles: ** {roles}\n"
        
        embed.description = personal_info + guild_info + roles
        await ctx.send(embed=embed)
