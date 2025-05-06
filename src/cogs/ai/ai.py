from io import BytesIO
import discord
from discord.ext import commands
import config
from core.cog import Cog
from main import MyBot
from groq import Groq
import requests
import time

class ArtificialIntelligence(Cog):
    def __init__(self, bot: MyBot):
        self.bot = bot
        self.emoji = config.emoji.cog_ai



    @commands.hybrid_command(name="gpt", description = "Ask to AI")
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.user)
    async def gpt(self, ctx: commands.Context, *, prompt:str):

        client = Groq(api_key=config.api.groq)
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.5,
            max_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )

        embed = discord.Embed()
        embed.title = prompt
        embed.description = completion.choices[0].message.content
        embed.set_author(name= self.bot.user.name, icon_url= self.bot.user.avatar.url)
        embed.set_footer(text = f"Requested by {ctx.author.name}", icon_url = ctx.author.avatar.url)
        await ctx.send(embed=embed)


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