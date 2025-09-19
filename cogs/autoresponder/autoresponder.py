import discord
from discord import app_commands
from discord.ext import commands
import config
from core.cog import Cog
from main import MyBot


class AutoResponder(Cog):
    def __init__(self, bot: MyBot):
        self.bot = bot
        self.emoji = config.emoji.cog_autoresponder



    autoresponder = app_commands.Group(
        name= "autoresponder", description= "autoresponder commands", guild_only= True
    )
    
    @autoresponder.command(name= "add", description= "set an auto-respond message")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(administrator = True)
    @app_commands.describe(trigger = "Message from the user", responce = "Reply from the bot", matchmode = "Type of auto respond")
    @app_commands.choices(matchmode = [
        app_commands.Choice(name = "exact", value = 1),
        app_commands.Choice(name = "includes", value = 2)
    ])

    async def add(self, interaction: discord.Interaction,*, trigger:str,  responce:str, matchmode: app_commands.Choice[int]):
        
        await interaction.response.defer(thinking=True)

        trigger = trigger.lower()
        matchmode = matchmode.name

        # checking for repeat in trigger
        data = self.bot.autoresponder_cache.get(interaction.guild.id, [])
        present_response = next((item for item in data if item["trigger"] == trigger), None)
        if present_response:
            return await interaction.followup.send(
                f'🔴 **Error:**\n "**{trigger}**" already present. Response for this trigger is : "**{present_response["responce"]}**"'
            )


        try:
            await self.bot.db["autoresponder"].insert_one({
                "guild_id": interaction.guild.id,
                "trigger" : trigger,
                "responce" : responce, 
                "matchmode" : matchmode
            })
            self.bot.autoresponder_cache.setdefault(interaction.guild.id, []).append({
                "trigger": trigger,
                "responce": responce,
                "matchmode": matchmode
        })
        except:
            return await interaction.followup.send("Something went wrong, please try again later")
        
        await interaction.followup.send(f'🟢 **Success:**\n Trigger: `{trigger}`, Responce: `{responce}`, Matchmode: `{matchmode}`')



    @autoresponder.command(name= "list", description= "shows the list of auto-respond messages")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(administrator = True)
    async def _list(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking= True)

        embed = discord.Embed()
        embed.title = "Auto-responder list"

        # Get data from cache
        data = self.bot.autoresponder_cache.get(interaction.guild.id)
        
        if not data:
            embed.description = "No auto-responder added for this server, use `/autoresponder add` to set"
            return await interaction.followup.send(embed=embed)

        description = ["**Trigger** `:` **Response** `:` **Matchmode**"] 

        # Process the cached data - now handling it as a list of dictionaries
        for index, item in enumerate(data, 1):
            trigger = item.get("trigger")
            response = item.get("responce") 
            matchmode = item.get("matchmode")
            description.append(f'{index}. **{trigger}** : **{response}** : `{matchmode}`')
        
        embed.description = "\n\n".join(description)
        await interaction.followup.send(embed=embed)



    @autoresponder.command(name= "delete", description= "delete an auto-respond messages")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(administrator = True)
    async def delete(self, interaction: discord.Interaction):
        author = interaction.user
        await interaction.response.defer(thinking = True)

        # Get data from cache
        cached_data = self.bot.autoresponder_cache.get(interaction.guild.id)

        if not cached_data:
            return await interaction.followup.send("🔴 No autoresponder for this server")
        
        # Get triggers from cached data
        triggers = [item["trigger"] for item in cached_data]
        ops = [discord.SelectOption(label=i, value=i) for i in triggers]

        dropdown = discord.ui.Select(options=ops, placeholder="Select a trigger", custom_id="dd")
        dropdown_view = discord.ui.View()
        dropdown_view.add_item(dropdown)

        msg1:discord.Message = await interaction.followup.send("**Please select the auto-respond you want to delete:**", view=dropdown_view)

        async def callback(interaction: discord.Interaction):
            await interaction.response.defer()

            if interaction.user != author:
                return await interaction.followup.send("You can't interact with this", ephemeral=True)
            
            # Find the selected trigger in cache
            selected_data = next((item for item in cached_data if item["trigger"] == dropdown.values[0]), None)

            embed = discord.Embed()
            embed.title = "Are you sure to delete the auto-responder?"  
            
            embed.add_field(name="Trigger", value=dropdown.values[0], inline=True)
            embed.add_field(name="Response", value=selected_data["responce"], inline=True)
            embed.add_field(name="Matchmode", value=f'`{selected_data["matchmode"]}`', inline=True)

            embed.set_footer(text=f'Requested by {interaction.user.name}', icon_url=interaction.user.avatar.url)

            delete = discord.ui.Button(label="Delete", style=discord.ButtonStyle.red)
            view = discord.ui.View()
            view.add_item(delete)

            await msg1.edit(embed=embed, view=view)
            
            async def btn_callback(interaction:discord.Interaction):
                await interaction.response.defer()

                if interaction.user != author:
                    return await interaction.followup.send("You can't interact with this", ephemeral=True)
                
                # Remove from database
                await self.bot.db["autoresponder"].delete_one({
                    "guild_id": interaction.guild.id,
                    "trigger": dropdown.values[0]
                })

                # Remove from cache
                self.bot.autoresponder_cache[interaction.guild.id] = [
                    item for item in cached_data if item["trigger"] != dropdown.values[0]
                ]

                await msg1.edit(embed=None, content=f'🟢 **Success:** Deleted the auto-responder for `{dropdown.values[0]}`', view=None)

            delete.callback = btn_callback

        dropdown.callback = callback

