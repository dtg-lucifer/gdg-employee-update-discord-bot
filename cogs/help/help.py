import discord
from discord.ext import commands
import config
import traceback,sys
import asyncio
from core.bot import MyBot
import os
from math import ceil
from typing import Optional


class Help(commands.Cog):
    cog_info = None
    def __init__(self, bot):
        self.bot:MyBot = bot
        # self.cog_info = cog_info
        self.all_app_commands = None
        self.emoji = config.emoji.cog_help
    
    @staticmethod
    def get_emoji(cog: commands.Cog):

        input = cog.emoji.split(":")
        list = []
        for i in input:
            list.append(i)

        input = str(list[2])
        list = []
        for char in input:
            if char.isdigit():
                list.append(char)

        output = int("".join(list))

        link = f"https://cdn.discordapp.com/emojis/{output}.png?=1"
        return link
    
    @commands.hybrid_command(
        name="help",
        with_app_command=True,
        help="Show all commands in bot",
        aliases=["h"]
    )
    @commands.cooldown(rate=10, per=60, type=commands.BucketType.user)
    async def help(self, ctx: commands.Context, command: Optional[str]):
        await ctx.defer()

        if command:
            try:
                cmd = self.bot.get_command(command)
                cog = cmd.cog
            except:
                return await ctx.send(embed=discord.Embed(
                    title="❌ Command Not Found",
                    description=f"**`{command}`** is not a valid command.",
                    colour=discord.Color.red()
                ))

            embed = discord.Embed(
                title=f"{config.emoji.dot} Command: `{cmd.name}`",
                colour=0x00e1ff
            )

            # Try to add cog emoji if available
            try:
                embed.set_thumbnail(url=self.get_emoji(cog))
            except:
                pass

            # Format aliases
            if cmd.aliases:
                alias_text = ", ".join(f"`{a}`" for a in cmd.aliases)
                aliases = f"{config.emoji.dot}**Aliases:** {alias_text}"
            else:
                aliases = ""

            # Extract arguments
            param = str(cmd.params).split("'")
            args = []
            for i in range(1, len(param), 2):
                if param[i] == "name":
                    continue
                args.append(f"<{param[i]}>")
            args_text = " ".join(args)

            # Set description and usage
            usage = f"`{config.bot.default_prefix}{cmd.name} {args_text}`"
            if cmd.description:
                embed.description = f"{config.emoji.dot} `{cmd.description}`\n\n{config.emoji.dot} **Usage:** {usage}\n{aliases}"
            else:
                embed.description = f"{config.emoji.dot} **Usage:** {usage}\n{aliases}"

            embed.set_footer(
                text="Made with ❤️ by Mainak",
                icon_url=self.bot.user.avatar.url
            )
            embed.set_author(
                name=self.bot.user.display_name,
                icon_url=self.bot.user.avatar.url
            )

            return await ctx.send(embed=embed)




        prefix = self.bot.prefix_cache.get(ctx.guild.id)
        if not prefix:
            prefix = config.bot.default_prefix
        try:
            # show all commands in cogs and their description and other info by group of the cogs
            # and show the help command of the bot
            # get all cogs if the cog has cog_info in it then show the cog_info

            async def get_home_embed():
                embed = discord.Embed(
                    color=discord.Color.red(),
                    description=""
                )
                try:
                    embed.set_image(url="https://files.catbox.moe/eusyb3.gif")
                except:
                    pass

                extra_cogs = []
                main_cogs = []
                hidden_cogs = []

                all_commands_names = []
                for cog in self.bot.cogs:
                    cog = self.bot.get_cog(cog)
                    for command in cog.get_commands():
                        all_commands_names.append(command.name)
                
                for cog in self.bot.cogs:
                    cog = self.bot.get_cog(cog)
                    if hasattr(cog,"cog_info"):
                        if not cog.cog_info:
                            continue
                        if cog.cog_info.hidden:
                            hidden_cogs.append(cog)
                        elif cog.cog_info.category.lower() == "main":
                            main_cogs.append(cog)
                        elif cog.cog_info.category.lower() == "extra":
                            extra_cogs.append(cog)
                if main_cogs:
                    embed.add_field(
                        name="__Main__",
                        value="\n".join([f"> **{cog.cog_info.emoji} : {cog.__cog_name__}**" for cog in main_cogs]),
                        inline=True
                    )
                if extra_cogs:
                    embed.add_field(
                        name="__Extra__",
                        value="\n".join([f"> **{cog.cog_info.emoji} : {cog.__cog_name__}**" for cog in extra_cogs]),
                        inline=True
                    )
                # if hidden_cogs:
                #     if checks.check_is_admin_predicate(ctx.author):
                #         embed.add_field(
                #             name="__Hidden__",
                #             value="\n".join([f"> - **{cog.cog_info.emoji}  {cog.__cog_name__} ({len(cog.get_commands())})**" for cog in hidden_cogs]),
                #             inline=False
                #         )

                cog_info = []
                for cog in self.bot.cogs:
                    cog = self.bot.get_cog(cog)
                    cog_info.append(cog)

                cog_info = "\n".join([f"{config.emoji.space}{config.emoji.dot}{cog.emoji} `:` {cog.__cog_name__}" for cog in cog_info if cog.__cog_name__ not in ["Dev", "Events", "Jishaku", "Error"]])
                    
                embed.description += f"{config.emoji.angular_arrow} __**General Info**__"
                embed.description += f"\n{config.emoji.space}{config.emoji.dot} Prefix for this server is ` {prefix} `"
                embed.description += f"\n{config.emoji.space}{config.emoji.dot} Total commands:  ` {len(all_commands_names)} `"
                embed.description += f"\n{config.emoji.space}{config.emoji.dot} [Get {self.bot.user.name}]({config.bot.invite_link}) | [Support server]({config.bot.support_invite}) | [Vote me]({config.bot.vote_link})"
                embed.description += "\n"
                embed.description += f"\n {config.emoji.angular_arrow} __**Features**__"
                embed.description += f"\n{cog_info}"
                

                embed.set_thumbnail(url=self.bot.user.display_avatar.url)
                embed.set_footer(
                    text=f"Made with ❤️ by Mainak",
                    icon_url=self.bot.user.display_avatar.url
                )
                embed.set_author(
                    name=f"{self.bot.user.display_name}",
                    icon_url=self.bot.user.display_avatar.url,
                )

                return embed

            timeout_time = 120
            cancled = False
            reported = False
            def reset_timeout(timeout:int=120):
                nonlocal timeout_time
                timeout_time = timeout

            async def get_home_view(disabled:bool=False):
                try:
                    view = discord.ui.View(timeout=120)
                    reset_timeout()

                    extra_cogs = []
                    main_cogs = []
                    hidden_cogs = []

                    all_commands_names = []
                    for cog in self.bot.cogs:
                        cog = self.bot.get_cog(cog)
                        for command in cog.get_commands():
                            all_commands_names.append(command.name)
                    

                    # for cog in self.bot.cogs:
                    #     cog = self.bot.get_cog(cog)
                    #     if hasattr(cog,"cog_info"):
                    #         if not cog.cog_info:
                    #             continue
                    #         if cog.cog_info.hidden:
                    #             hidden_cogs.append(cog)
                    #         elif cog.cog_info.category.lower() == "main":
                    #             main_cogs.append(cog)
                    #         elif cog.cog_info.category.lower() == "extra":
                    #             extra_cogs.append(cog)

                    for cog in self.bot.cogs:
                        cog = self.bot.get_cog(cog)
                        if cog.__cog_name__ not in ["Dev", "Events", "Jishaku", "Error"]:
                            main_cogs.append(cog)
                    
                    all_commands_button = discord.ui.Button(
                        label="All Commands",
                        style=discord.ButtonStyle.green,
                        #emoji=#self.bot.emoji.COMMANDS,
                        row=1
                    )
                    all_commands_button.callback = lambda i: all_commands_button_callback(i)
                    # view.add_item(all_commands_button)

                    report_button = discord.ui.Button(
                        label="Report",
                        style=discord.ButtonStyle.red,
                        row=1
                    )
                    report_button.callback = lambda i: report_button_callback(i)
                    if reported:
                        report_button.disabled = True
                    # view.add_item(report_button)

                    combined_cogs = main_cogs + extra_cogs

                    if combined_cogs:  # Check if there are any cogs to display
                        main_select_categorie = discord.ui.Select(
                            placeholder="Select a category to view",
                            options=[discord.SelectOption(
                                label=cog.__cog_name__,
                                value=cog.__cog_name__,
                                description=cog.description if cog.description else "No description",
                                emoji=cog.emoji
                            ) for cog in combined_cogs],
                            row=0
                        )
                        main_select_categorie.callback = lambda i: select_categorie_callback(i)
                        view.add_item(main_select_categorie)


                    invite_me_button = discord.ui.Button(
                        label="Invite",
                        style=discord.ButtonStyle.link,
                        url = config.bot.invite_link,
                        row=2,
                        emoji=config.emoji.invite
                    )
                    view.add_item(invite_me_button)

                    support_server_button = discord.ui.Button(
                        label="Support",
                        style=discord.ButtonStyle.link,
                        url=config.bot.support_invite,
                        row=2,
                        emoji=config.emoji.cog_help
                    )
                    view.add_item(support_server_button)

                    if disabled:
                        for item in view.children:
                            item.disabled = True
                    return view
                except Exception as e:
                    print(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                    return
                
            async def report_button_callback(interaction:discord.Interaction):
                try:
                    if interaction.user.id != ctx.author.id:
                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this button",
                                color=discord.Color.red()
                            ),
                            ephemeral=True,
                            delete_after=10
                        )
                    
                    class report_submit_modal(discord.ui.Modal,title="Submit Report"):
                        report_title_field = discord.ui.TextInput(
                            placeholder="Report Title",
                            label="Report Title",
                            required=True,
                            row=0,
                            style=discord.TextStyle.short
                        )
                        report_description_field = discord.ui.TextInput(
                            placeholder="Report Description",
                            label="Report Description",
                            required=True,
                            row=1,
                            style=discord.TextStyle.long
                        )
                        report_attachment_field = discord.ui.TextInput(
                            placeholder="Saparate the links with comma",
                            label="Report Attachment links",
                            required=False,
                            row=2,
                            style=discord.TextStyle.long
                        )
                        bot = self.bot
                        async def on_submit(self,interaction:discord.Interaction):
                            try:
                                title = self.report_title_field.value
                                description = self.report_description_field.value
                                attachments = self.report_attachment_field.value.split(",")
                                if not title or not description:
                                    return await interaction.response.send_message(
                                        embed=discord.Embed(
                                            description="Title and Description are required",
                                            color=discord.Color.red()
                                        ),
                                        ephemeral=True,
                                        delete_after=10
                                    )
                                embed = discord.Embed(
                                    title=title,
                                    description=description,
                                    color=discord.Color.red()
                                )
                                if attachments:
                                    embed.add_field(
                                        name="Attachments links",
                                        value="\n".join(attachments),
                                        inline=False
                                    )
                                embed.set_footer(
                                    text=f"Reported by {interaction.user.display_name} | {interaction.user.id}",
                                    icon_url=interaction.user.display_avatar.url
                                )
                                embed.set_author(
                                    name=f"{ctx.author.display_name}",
                                    icon_url=ctx.author.display_avatar.url
                                )
                                await interaction.response.defer(thinking=True,ephemeral=True)
                                channel = self.bot.get_channel(self.bot.channels.report_channel)
                                if not channel:
                                    return print(f"Report channel not found. Channel ID: {self.bot.channels.report_channel}")
                                await channel.send(embed=embed)
                                nonlocal reported
                                reported = True
                                await interaction.edit_original_response(embed=discord.Embed(
                                    description="Report submitted successfully",
                                    color=discord.Color.red()
                                ))
                            except Exception as e:
                                print(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                    
                    await interaction.response.send_modal(report_submit_modal())

                except Exception as e:
                    print(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")


            async def all_commands_button_callback(interaction:discord.Interaction):
                try:
                    if interaction.user.id != ctx.author.id:
                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this button",
                                color=discord.Color.red()
                            ),
                            ephemeral=True,
                            delete_after=10
                        )
                    extra_cogs = []
                    main_cogs = []
                    hidden_cogs = []

                    all_commands_names = []
                    for cog in self.bot.cogs:
                        cog = self.bot.get_cog(cog)
                        for command in cog.get_commands():
                            all_commands_names.append(command.name)
                    for cog in self.bot.cogs:
                        cog = self.bot.get_cog(cog)
                        if hasattr(cog,"cog_info"):
                            if not cog.cog_info:
                                continue
                            if cog.cog_info.hidden:
                                hidden_cogs.append(cog)
                            elif cog.cog_info.category.lower() == "main":
                                main_cogs.append(cog)
                            elif cog.cog_info.category.lower() == "extra":
                                extra_cogs.append(cog)
                    
                    embed = discord.Embed(
                        color=discord.Color.red()
                    )
                    for cog in main_cogs+extra_cogs:
                        embed.add_field(
                            name=f"**{cog.cog_info.emoji} {cog.__cog_name__} [{len(cog.get_commands())}]**",
                            value=" | ".join([f"**`{command.name}`**" for command in cog.get_commands()]),
                            inline=False
                        )
                    embed.set_footer(
                        text=f"Made with ❤️ by Mainak",
                        icon_url=self.bot.user.display_avatar.url
                    )
                    embed.set_author(
                        name=f"{self.bot.user.display_name}",
                        icon_url=self.bot.user.display_avatar.url,
                    )
                    embed.set_thumbnail(url=self.bot.user.display_avatar.url)
                    await interaction.response.edit_message(embed=embed,view=await get_home_view(disabled=True))
                except Exception as e:
                    print(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
            

            async def select_categorie_callback(interaction:discord.Interaction):
                try:
                    if interaction.user.id != ctx.author.id:
                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this select menu",
                                color=discord.Color.red()
                            ),
                            ephemeral=True,
                            delete_after=10
                        )
                    value = interaction.data["values"][0]
                    
                    def get_selected_cog(name: str):
                        for cog_name, cog in self.bot.cogs.items():                            
                            if cog_name.lower() == name.lower():
                                return cog
                        return None
                        
                    cog = get_selected_cog(value)

                    async def get_selected_cog_embed(cog: commands.Cog, page: int = 0, per_page: int = 10):
                        try:
                            embed = discord.Embed(
                                title=f"{cog.__cog_name__} Commands",
                                description=f"{cog.description if cog.description else ''}",
                                color=discord.Color.red()
                            )
                            all_commands = cog.get_commands()
                            total_commands = len(all_commands)

                            # Pagination logic
                            if total_commands > 0:
                                max_page = ceil(total_commands / per_page)
                                start = page * per_page
                                end = start + per_page
                                commands_page = all_commands[start:end]
                                embed.description += (
                                    "\n" +
                                    "\n".join([f"> **`{command.name}`** - {command.description or 'No description'}" for command in commands_page])
                                )
                                if max_page > 1:
                                    embed.set_footer(
                                        text=f"Page {page+1}/{max_page} • Made with ❤️ by Mainak",
                                        icon_url=self.bot.user.display_avatar.url
                                    )
                                else:
                                    embed.set_footer(
                                        text=f"Made with ❤️ by Mainak",
                                        icon_url=self.bot.user.display_avatar.url
                                    )
                            else:
                                embed.description += "\n> No commands found in this category."
                                embed.set_footer(
                                    text=f"Made with ❤️ by Mainak",
                                    icon_url=self.bot.user.display_avatar.url
                                )

                            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
                            embed.set_author(
                                name=f"{self.bot.user.display_name}",
                                icon_url=self.bot.user.display_avatar.url,
                            )
                            return embed
                        except Exception as e:
                            print(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                            return None

                    async def get_selected_cog_view(disabled: bool = False, page: int = 0, per_page: int = 10):
                        try:
                            view = discord.ui.View(timeout=120)
                            reset_timeout()
                            all_commands = cog.get_commands()
                            total_commands = len(all_commands)
                            max_page = ceil(total_commands / per_page) if total_commands else 1

                            # Pagination buttons
                            if total_commands > per_page:
                                prev_button = discord.ui.Button(
                                    style=discord.ButtonStyle.secondary,
                                    emoji="⬅️",
                                    row=0,
                                    disabled=disabled or page == 0
                                )
                                next_button = discord.ui.Button(
                                    style=discord.ButtonStyle.secondary,
                                    emoji="➡️",
                                    row=0,
                                    disabled=disabled or (page + 1) >= max_page
                                )

                                async def prev_callback(interaction):
                                    if interaction.user.id != ctx.author.id:
                                        return await interaction.response.send_message(
                                            embed=discord.Embed(
                                                description="You are not allowed to use this button",
                                                color=discord.Color.red()
                                            ),
                                            ephemeral=True,
                                            delete_after=10
                                        )
                                    await interaction.response.edit_message(
                                        embed=await get_selected_cog_embed(cog, page=page-1, per_page=per_page),
                                        view=await get_selected_cog_view(disabled, page=page-1, per_page=per_page)
                                    )

                                async def next_callback(interaction):
                                    if interaction.user.id != ctx.author.id:
                                        return await interaction.response.send_message(
                                            embed=discord.Embed(
                                                description="You are not allowed to use this button",
                                                color=discord.Color.red()
                                            ),
                                            ephemeral=True,
                                            delete_after=10
                                        )
                                    await interaction.response.edit_message(
                                        embed=await get_selected_cog_embed(cog, page=page+1, per_page=per_page),
                                        view=await get_selected_cog_view(disabled, page=page+1, per_page=per_page)
                                    )

                                prev_button.callback = prev_callback
                                next_button.callback = next_callback
                                view.add_item(prev_button)
                                view.add_item(next_button)

                            # Command select dropdown (for current page)
                            commands_page = all_commands[page*per_page:(page+1)*per_page]
                            if commands_page:
                                command_select = discord.ui.Select(
                                    placeholder="Select a command to view",
                                    options=[
                                        discord.SelectOption(
                                            label=command.name,
                                            value=command.name,
                                            description=command.description if command.description else "No description"
                                        ) for command in commands_page
                                    ],
                                    row=1
                                )

                                async def command_select_callback(interaction):
                                    if interaction.user.id != ctx.author.id:
                                        return await interaction.response.send_message(
                                            embed=discord.Embed(
                                                description="You are not allowed to use this select menu",
                                                color=discord.Color.red()
                                            ),
                                            ephemeral=True,
                                            delete_after=10
                                        )
                                    value = interaction.data["values"][0]
                                    command = next((cmd for cmd in all_commands if cmd.name == value), None)
                                    if not command:
                                        return await interaction.response.send_message(
                                            embed=discord.Embed(
                                                description="Command not found",
                                                color=discord.Color.red()
                                            ),
                                            ephemeral=True,
                                            delete_after=10
                                        )

                                    async def get_selected_command_embed():
                                        try:
                                            embed = discord.Embed(
                                                title=f"{command.name} Command",
                                                description=f"{command.description}" if command.description else "",
                                                color=discord.Color.red()
                                            )
                                            if not self.all_app_commands:
                                                self.all_app_commands = await self.bot.tree.fetch_commands()

                                            def get_app_command(name):
                                                for cmd in self.all_app_commands:
                                                    if cmd.name == name:
                                                        return cmd
                                                return None

                                            app_command = get_app_command(command.name)

                                            if app_command:
                                                if app_command.options:
                                                    embed.description += f"\n\n**• Primary Command:** `{prefix}{app_command.name} {' '.join([f'<{arg}>' for arg in command.clean_params])}`"
                                                    embed.description += f"\n\n**• Options:**\n"
                                                    for option in app_command.options:
                                                        embed.description += f"\n> {option.mention if hasattr(option,'mention') else f'{prefix}{command.name} {option.name}'}\n> {option.description}\n"
                                                else:
                                                    embed.description += f"\n\n**• Primary Command:** {app_command.mention if hasattr(app_command,'mention') else f'{prefix}{command.name}'}"
                                            else:
                                                embed.description += f"\n\n**• Primary Command:** `{prefix}{command.name} {' '.join([f'<{arg}>' for arg in command.clean_params])}`"
                                                if hasattr(command, "commands"):
                                                    embed.description += f"\n\n**• Subcommands:**\n"
                                                    for subcommand in command.commands:
                                                        embed.description += f"\n> **`{prefix}{command.name} {subcommand.name} {' '.join([f'<{arg}>' for arg in subcommand.clean_params])}`** \n> {subcommand.description}\n"

                                            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
                                            embed.set_footer(
                                                text=f"Made with ❤️ by Mainak",
                                                icon_url=self.bot.user.display_avatar.url
                                            )
                                            embed.set_author(
                                                name=f"{self.bot.user.display_name}",
                                                icon_url=self.bot.user.display_avatar.url,
                                            )
                                            return embed
                                        except Exception as e:
                                            print(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                                            return None

                                    async def get_selected_command_view(disabled: bool = False):
                                        try:
                                            view = discord.ui.View(timeout=120)
                                            reset_timeout()
                                            back_button = discord.ui.Button(
                                                style=discord.ButtonStyle.secondary,
                                                row=1,
                                                emoji=config.emoji.back
                                            )
                                            async def back_button_callback(interaction):
                                                if interaction.user.id != ctx.author.id:
                                                    return await interaction.response.send_message(
                                                        embed=discord.Embed(
                                                            description="You are not allowed to use this select menu",
                                                            color=discord.Color.red()
                                                        ),
                                                        ephemeral=True,
                                                        delete_after=10
                                                    )
                                                await interaction.response.edit_message(
                                                    embed=await get_selected_cog_embed(cog, page=page, per_page=per_page),
                                                    view=await get_selected_cog_view(disabled, page=page, per_page=per_page)
                                                )
                                            back_button.callback = back_button_callback
                                            view.add_item(back_button)
                                            if disabled:
                                                for item in view.children:
                                                    item.disabled = True
                                            return view
                                        except Exception as e:
                                            print(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                                            return None

                                    await interaction.response.edit_message(
                                        embed=await get_selected_command_embed(),
                                        view=await get_selected_command_view()
                                    )

                                command_select.callback = command_select_callback
                                view.add_item(command_select)

                            back_button = discord.ui.Button(
                                style=discord.ButtonStyle.secondary,
                                row=2,
                                emoji=config.emoji.back
                            )

                            async def back_button_callback(interaction):
                                if interaction.user.id != ctx.author.id:
                                    return await interaction.response.send_message(
                                        embed=discord.Embed(
                                            description="You are not allowed to use this select menu",
                                            color=discord.Color.red()
                                        ),
                                        ephemeral=True,
                                        delete_after=10
                                    )
                                await interaction.response.edit_message(
                                    embed=await get_home_embed(),
                                    view=await get_home_view()
                                )

                            back_button.callback = back_button_callback
                            view.add_item(back_button)

                            if disabled:
                                for item in view.children:
                                    item.disabled = True

                            return view
                        except Exception as e:
                            print(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                            return None
                    async def back_button_callback(interaction:discord.Interaction):
                        try:
                            if interaction.user.id != ctx.author.id:
                                return await interaction.response.send_message(
                                    embed=discord.Embed(
                                        description="You are not allowed to use this select menu",
                                        color=discord.Color.red()
                                    ),
                                    ephemeral=True,
                                    delete_after=10
                                )
                            await interaction.response.edit_message(embed=await get_home_embed(),view=await get_home_view())
                        except Exception as e:
                            print(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}")
                    await interaction.response.edit_message(embed=await get_selected_cog_embed(cog),view=await get_selected_cog_view(disabled=False))
                except Exception as e:
                    print(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")

            message = await ctx.send(embed=await get_home_embed(),view=await get_home_view())

            while not cancled:
                timeout_time -= 1
                if timeout_time <= 0:
                    try:
                        await message.edit(embed=await get_home_embed(),view=await get_home_view(disabled=True))
                    except:
                        pass
                    break
                await asyncio.sleep(1)
        except Exception as e:
            print(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")



    @commands.hybrid_command(name= "mail", description = "Send us a message")
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.user)
    async def mail(self, ctx:commands.Context,*, message: str):

        msg_log_channel = self.bot.get_channel(config.loging_channels.mail)

        embed = discord.Embed()
        embed.title = ctx.author.display_name
        embed.set_thumbnail(url=ctx.author.avatar.url)
        embed.color=config.color.no_color
        embed.add_field(name="User Mention:", value = ctx.author.mention, inline= False)
        embed.add_field(name="User Name:", value = ctx.author.name, inline= False)
        embed.add_field(name="ID:", value = ctx.author.id, inline= False)


        if not isinstance(ctx.channel, discord.channel.DMChannel):
            
            embed.add_field(name="Guild Name:", value = ctx.guild.name, inline = False)
            embed.add_field(name="Guild ID:", value = ctx.guild.id, inline= False)
        
        embed.description = f"**Message:** {message}"

        await msg_log_channel.send(embed=embed)


        resp_embed = discord.Embed()
        resp_embed.color=config.color.no_color
        resp_embed.title = "Your message has been recieved"
        resp_embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
        resp_embed.description = f"{config.emoji.arrow} **We will reply you shortly**\n{config.emoji.arrow} **MSG:** {message} "
        await ctx.reply(embed=resp_embed)


    @commands.command(name="botinfo", aliases=["developer", "bot_info", "info"])
    async def botinfo(self, ctx: commands.Context):
        def get_stats() -> discord.Embed:
            bot_info = f"> **Bot Tag:** {self.bot.user.name}\n> **Bot Mention:** {self.bot.user.mention}\n"
            uptime = f"> **Uptime:** <t:{int(self.bot.uptime)}:R>\n"
            stats = f"> **Servers:** {len(self.bot.guilds)}\n> **Users:** {len(self.bot.users)}\n"
            os_info = f"> **Operating System:** {os.name}\n> **Code Language:** Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}\n> **Discord.py:** {discord.__version__}\n"
            embed = discord.Embed(color=discord.Color.brand_red())
            embed.description = bot_info + uptime + stats + os_info
            return embed

        def get_dev() -> discord.Embed:
            embed = discord.Embed(color=discord.Color.brand_green())
            dev = f"> **Created by**: [Mainak](https://discord.com/users/510002835140771842)\n"
            server = f"> **Developed at**: [Coders For Coders]({config.bot.support_invite})\n"
            website = f"> **Website**: [Homie]({config.bot.website})\n"
            topgg = f"> **Top.GG**: [Homie]({config.bot.vote_link})\n"
            mail = f"\n{config.emoji.arrow} Use `mail` command if you want to send us a message"
            embed.description = dev + server + website + topgg + mail
            return embed

        view = discord.ui.View(timeout=120)
        
        stats_btn = discord.ui.Button(label="Stats", style=discord.ButtonStyle.primary)
        dev_btn = discord.ui.Button(label="Developer", style=discord.ButtonStyle.success)

        async def stats_btn_callback(interaction: discord.Interaction):
            if interaction.user.id != ctx.author.id:
                return await interaction.response.send_message("> You can't use this button", ephemeral=True)
            await interaction.response.edit_message(embed=get_stats(), view=view)

        async def dev_btn_callback(interaction: discord.Interaction):
            if interaction.user.id != ctx.author.id:
                return await interaction.response.send_message("> You can't use this button", ephemeral=True)
            await interaction.response.edit_message(embed=get_dev(), view=view)

        stats_btn.callback = stats_btn_callback
        dev_btn.callback = dev_btn_callback

        view.add_item(stats_btn)
        view.add_item(dev_btn)

        message = await ctx.send(embed=get_stats(), view=view)

        async def disable_on_timeout():
            await view.wait()  
            for item in view.children:
                item.disabled = True
            await message.edit(view=view)

        self.bot.loop.create_task(disable_on_timeout())
