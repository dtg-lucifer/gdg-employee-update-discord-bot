import discord
from discord.ext import commands
from core.cog import Cog
from core.bot import MyBot
import config
import time

class Error(Cog):
    def __init__(self, bot: MyBot):
        self.bot = bot
        self.emoji = "⚠️"
        self.cooldown_warned = {}


    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):       
        
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.message.add_reaction("⚠")
            embed = discord.Embed()
            embed.title = ctx.command.name
            embed.colour = discord.Colour.red()
            
            if ctx.command.aliases:
                alias = f"Aliases: {ctx.command.aliases}\n"
            else:
                alias = ""
            
            prefix = self.bot.prefix_cache.get(ctx.guild.id)

            if prefix == None:
                prefix = config.bot.default_prefix
  
            embed.description = f" {alias} **Example:**\n {prefix}{ctx.command.name} {{{error.param.name}}}"
            return await(ctx.send( f"**Missing required argument:** `{error.param.name}`", embed=embed))
            

        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(f"You need `{error.missing_permissions}` for this command")

        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(f"Bot needs {error.missing_permissions} for this command")


        elif isinstance(error, commands.CommandOnCooldown):
            key = (ctx.guild.id, ctx.author.id, ctx.command.name)
            current_time = time.time()

            # Check if we've already warned this user for this command cooldown
            cooldown_reset_time = self.cooldown_warned.get(key, 0)
            if current_time >= cooldown_reset_time:
                # They haven't been warned recently, or their cooldown expired
                self.cooldown_warned[key] = current_time + error.retry_after

                await ctx.send(
                    f"You are on cooldown, please try again in `{int(error.retry_after)}` seconds.",
                    delete_after=3.0
                )
            else:
                pass

        elif isinstance(error, commands.NotOwner):
            return
        
        elif isinstance(error, commands.CommandNotFound):
            return #await(ctx.send("This command doesn't exist 🐒"))
                 
        else:
            channel = self.bot.get_channel(config.loging_channels.error_log)
            embed = discord.Embed(title="Error", color=config.color.no_color)
            embed.add_field(name="User", value=ctx.author.name)
            embed.add_field(name="Guild", value=ctx.guild.name)
            embed.add_field(name="uid", value=ctx.author.id)
            embed.add_field(name="gid", value=ctx.guild.id)
            embed.add_field(name="Command", value=ctx.command)
            embed.add_field(name="Error", value=error)
            await channel.send(embed=embed)
        