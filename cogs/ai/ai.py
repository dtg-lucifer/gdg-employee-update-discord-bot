from io import BytesIO
import discord
from discord.ext import commands
import config
from core.cog import Cog
from main import MyBot
from groq import Groq
import requests
import time
import os

class ArtificialIntelligence(Cog):
    def __init__(self, bot: MyBot):
        self.bot = bot
        self.emoji = config.emoji.cog_ai



    @commands.hybrid_command(name="gpt", description="Ask AI")
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.user)
    async def gpt(self, ctx: commands.Context, *, prompt: str):
        models = [
            {"name": "llama-3.1-8b-instant", "display_name": "LLaMA 3.1 8B Instant", "emoji": config.emoji.metaai},
            {"name": "openai/gpt-oss-20b", "display_name": "Chat GPT", "emoji": config.emoji.chatgpt},
            {"name": "groq/compound", "display_name": "GroQ Compound", "emoji": config.emoji.groq}
        ]

        embed = discord.Embed(title="Select your model")
        view = discord.ui.View()

        for model in models:
            button = discord.ui.Button(  
                label="",
                style=discord.ButtonStyle.secondary,
                emoji=model["emoji"],
            )

            async def callback(interaction: discord.Interaction, m=model["name"]):
                if interaction.user.id != ctx.author.id:
                    await interaction.response.send_message(
                        "This is not your selection!", ephemeral=True
                    )
                    return

                await interaction.response.defer()

                client = Groq(api_key=config.api.groq)
                completion = client.chat.completions.create(
                    model=m,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.5,
                    max_tokens=1024,
                )

                response_text = completion.choices[0].message.content

                embed_reply = discord.Embed(
                    title=prompt, description=response_text
                )
                embed_reply.set_author(
                    name=self.bot.user.name, icon_url=self.bot.user.avatar.url
                )
                embed_reply.set_footer(
                    text=f"Requested by {ctx.author.name}    |    Model: {m}",
                    icon_url=ctx.author.avatar.url,
                )

                try:
                    await msg.delete()
                except:
                    pass
                try:
                    await ctx.send(embed=embed_reply)
                except discord.HTTPException:
                    filename = f"{ctx.message.id}.txt"
                    with open(f"tempFiles/{filename}", "w", encoding="utf-8") as f:
                        f.write(response_text)

                    file = discord.File(
                        f"tempFiles/{filename}", filename="response.txt"
                    )
                    await ctx.send(
                        "Response exceeded character limit, content has been written to the text file",
                        file=file,
                    )
                    os.remove(f"tempFiles/{filename}")

            button.callback = callback
            view.add_item(button)

        msg: discord.Message = await ctx.send(embed=embed, view=view)


    @commands.hybrid_command(name="image", description="Generate an image using Stable Diffusion")
    async def image(self, ctx: commands.Context, *, prompt: str):
        tm = time.time()
        msg: discord.Message = await ctx.send(f"⌛Generating your image...\n**ETA:** <t:{int(time.time()+20)}:R>")
        url = "https://api.segmind.com/v1/luma-photon-flash-txt-2-img"

        data = {
        "prompt": prompt,
        "aspect_ratio": "1:1"
        }
        headers = {'x-api-key': config.api.image}
        response = requests.post(url, json=data, headers=headers)
        await msg.delete()
        tm = round(time.time() - tm, 2)

        await ctx.send(content=f"**Prompt:** `{prompt}`\n**Time:** `{tm} sec`",file=discord.File(fp=BytesIO(response.content), filename="image.png"))