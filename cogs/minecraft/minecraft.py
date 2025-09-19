import discord
from discord.ext import commands
from core.cog import Cog
from core.bot import MyBot
import config
from typing import Optional
import requests


class Minecraft(Cog):
    def __init__(self, bot: MyBot):
        self.bot = bot
        self.emoji = config.emoji.cog_minecraft


    @commands.command(name="minecraft", description = "Get the information of a minecraft server", aliases = ["mc"])
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.user)
    async def minecraft(self, ctx: commands.Context, ip: str):

        link = f"https://api.mcstatus.io/v2/status/java/{ip}"

        data = requests.get(url=link)
        data= data.json()

        embed = discord.Embed()

        embed.title = " "

        try:
            status = data['version']['name_clean']
            embed.color = discord.Colour.red()

            if status == "● Offline":
                embed.add_field(name="Status", value=status, inline=False)
                return await ctx.send(embed=embed)
        except:
            embed.color = discord.Colour.red()
            embed.add_field(name="Status", value="● Offline", inline=False)
            await ctx.send(embed=embed)
            return
        
        embed.color = discord.Colour.green()
        version = data['version']['name_clean']
        online_players = data['players']['online']
        max_players = data['players']['max']
        status = data['motd']['clean']

        embed.add_field(name="Status", value="● Online", inline=False)
        embed.add_field(name="version", value=version, inline=False)
        embed.add_field(name="Online Players", value=online_players, inline=False)
        embed.add_field(name="Max Players", value=max_players, inline=False)
        embed.add_field(name="Status", value=status, inline=False)

        await ctx.send(embed=embed)


    @commands.command(name="mcserver", description = "Set a default mc ip for your guild")
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.user)
    async def mcserver(self, ctx: commands.Context, ip: Optional[str]):
        
        if ip:
            if not ctx.author.guild_permissions.administrator:
                await ctx.reply("You need `Administrator` permission to set the ip")
                return
            
            await self.bot.db["minecraft"].update_one(

                filter={"guild_id" : ctx.guild.id,},
                update={"$set" : {"ip" : ip}},
                upsert=True
            )

            await ctx.send("**🟢 Success:** The ip has been recorded for this guild. \n Use can now use `mcserver` command for the stats")
        
        ip = await self.bot.db["minecraft"].find_one(filter={"guild_id":ctx.guild.id})

        if not ip:
            await ctx.send("Please set an ip for first time for this guild")
            return

        ip = ip["ip"]
        link = f"https://api.mcstatus.io/v2/status/java/{ip}"

        data = requests.get(url=link)
        data= data.json()

        embed = discord.Embed()

        embed.title = " "

        try:
            status = data['version']['name_clean']
            embed.color = discord.Colour.red()

            if status == "● Offline":
                embed.add_field(name="Status", value=status, inline=False)
                

                return await ctx.send(embed=embed)
        except:
            embed.color = discord.Colour.red()
            embed.add_field(name="Status", value="● Offline", inline=False)
            await ctx.send(embed=embed)
            return
        
        embed.color = discord.Colour.green()
        version = data['version']['name_clean']
        online_players = data['players']['online']
        max_players = data['players']['max']
        status = data['motd']['clean']
        players: list = data['players']['list']

        embed.add_field(name="Status", value="● Online", inline=False)
        embed.add_field(name="version", value=version, inline=False)
        embed.add_field(name="Online Players", value=online_players, inline=False)
        embed.add_field(name="Max Players", value=max_players, inline=False)
        embed.add_field(name="Status", value=status, inline=False)

        if len(players) > 0:
            count = 1
            for i in players:
                embed.add_field(name=f"Player {count}", value=i['name_clean'], inline=False)
                count = count+1

        await ctx.send(embed=embed)