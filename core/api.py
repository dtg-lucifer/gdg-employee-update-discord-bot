import discord
from discord.ext import commands
from fastapi import FastAPI, HTTPException, Request, Response, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
import config

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != config.api.dash:
        raise HTTPException(status_code=403, detail="Unauthorized")


bot: commands.Bot | None = None

def set_bot_instance(bot_instance: commands.Bot):
    global bot
    bot = bot_instance

@app.get("/")
async def root():
    return {"msg":"Hello world"}

@app.get("/stats", dependencies = [Depends(verify_api_key)])
async def ping():
    name = bot.user.name
    ping = round(bot.latency * 1000, 2)
    guild_count = len(bot.guilds)
    user_count = len(bot.users)
    commands = len(bot.commands)

    return {
        "name":name,
        "ping":ping,
        "guilds":guild_count,
        "users":user_count,
        "commands":commands
    }

@app.get("/guilds", dependencies = [Depends(verify_api_key)])
async def get_guilds(request: Request):

    guild_id = request.query_params.get("guild_id")

    if not guild_id:
        return [{"id": guild.id, "name": guild.name} for guild in bot.guilds]

    guild = bot.get_guild(int(guild_id))
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")

    return {
        "id": guild.id,
        "name": guild.name,
        "member_count": guild.member_count,
        "owner": guild.owner.id
    }

@app.get("/guilds/{guild_id}/members", dependencies = [Depends(verify_api_key)])
async def get_guild_members(guild_id: str):
    guild = bot.get_guild(int(guild_id))
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")

    return [
        {
            "id": member.id,
            "name": member.name,
            "discriminator": member.discriminator,
            "avatar": member.avatar.url if member.avatar else None
        }
        for member in guild.members
    ]

@app.get("/users/{user_id}", dependencies = [Depends(verify_api_key)])
async def get_user_info(user_id: str):
    guild = bot.get_guild(int(config.guild.id))
    user: discord.User = guild.get_member(int(user_id)) if guild else None
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "name": user.name,
        "discriminator": user.discriminator,
        "avatar": user.avatar.url if user.avatar else None
    }

@app.get("/users/perms/isadmin", dependencies = [Depends(verify_api_key)])
async def is_user_admin(request: Request):

    user_id = request.query_params.get("user_id")
    guild = request.query_params.get("guild_id", config.guild.id)
    guild = bot.get_guild(int(guild))
    user = guild.get_member(int(user_id)) if guild else None
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "name": user.name,
        "is_admin": user.guild_permissions.administrator
    }
@app.get("/users/perms/isowner", dependencies = [Depends(verify_api_key)])
async def is_user_owner(request: Request):
    user_id = request.query_params.get("user_id")
    guild_id = request.query_params.get("guild_id")
    guild = bot.get_guild(int(guild_id))
    user = guild.get_member(int(user_id)) if guild else None
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "name": user.name,
        "is_owner": user.id == guild.owner_id
    }

@app.get("/users/perms/manage_server", dependencies = [Depends(verify_api_key)])
async def can_user_manage_server(request: Request):
    user_id = request.query_params.get("user_id")
    guild_id = request.query_params.get("guild_id", config.guild.id)
    guild = bot.get_guild(int(guild_id))
    user = guild.get_member(int(user_id)) if guild else None
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "name": user.name,
        "manage_server": user.guild_permissions.manage_guild
    }

@app.get("/commands", dependencies=[Depends(verify_api_key)])
async def get_commands():
    output = []
    for command in bot.commands:
        params = {}
        for name, param in command.params.items():
            params[name] = {
                "name": param.name,
                "kind": str(param.kind),
                "default": str(param.default) if param.default != param.empty else None,
                "annotation": str(param.annotation) if param.annotation != param.empty else None,
            }

        data = {
            "name": command.name if command.name else None,
            "description": command.description if command.description else None,
            "aliases": list(command.aliases) if command.aliases else [],
            "params": params if params else None,
        }
        output.append(data)

    return output
