from os import getenv
from dotenv import load_dotenv

load_dotenv()

class bot:
    token = getenv("Discord_Token")
    default_prefix = "g."
    api = True
    owner_ids = {int(x.strip()) for x in getenv("OWNER_ID", "").split(",") if x.strip()}
    default_status = "Welcome to GDG on campus TIU!"
    cogs = [
        "jishaku",
        "admin",
        "ai",
        "autoresponder",
        "error",
        "events",
        "help",
        "level",
        "minecraft",
        "tools",
    ]

    support_invite = "http://localhost"
    invite_link = "http://localhost"
    vote_link = "http://localhost"
    website = "http://localhost"

class database:
    token = getenv("MONGO_URI")
    db_name = "gdg_bot"
    # pgsql = getenv("PGSQL")

class api:
    weather = getenv("WEATHER_API")
    groq = getenv("GROQ")
    remove_bg = getenv("REMOVE_BG")
    image = getenv("IMAGE")
    # dash = getenv("DASH_API")
    
# class server:
#     host = str(getenv("SERVER_HOST"))
#     port = int(getenv("SERVER_PORT"))


class level:
    xp_per_message = 1
    base_xp = 10
    growth_rate = 1.2

class emoji:

    bot_ping = "<:bot_ping:1267199109027201147>"
    db_ping = "<:db_ping:1267199058913660929>"
    lavalink_ping = "<:lava_ping:1270432997069291561>"
    music_filter = "<:music:1270434659750117416>"
    arrow = "<:new_arrow:1276772471252586639>"
    developer = "<:developer:1288934616480219226>"
    cache = "<:cache:1362040419957084373>"
    space = "<:empty_space:1362810768826961961>"
    back = "<:back:1367582929211101274>"
    angular_arrow = "<:angular_right:1367582937813483541>"
    invite = "<:link:1367582934953103413>"
    dot = "<:dot:1367588950146814093>"


    chatgpt = "<:chatgpt:1413170679645208799>"
    metaai = "<:metaai:1413172562049110087>"
    groq  = "<:groq:1413174326433419294>"

    cog_admin = "<:admin:1262364323666202714>"
    cog_ai = "<:ai:1262364370474897489>"
    cog_autoresponder = "<:ai:1262364370474897489>"
    cog_fun_tools = "<:fun_tools:1255550320478781471>"
    cog_gif_commands = "<:gif:1254019441503633408>"
    cog_help = "<:help:1262364412497498164>"
    cog_image_tools = "<:image_tool:1254019503659028581>"
    cog_lovecalc = "<:love_calc:1254019519878402080>"
    cog_minecraft = "<:Minecraft:1277279364316139601>"
    cog_music = "<:music:1270434659750117416>"
    cog_text_tools = "<:text_tool:1254019510533623850>"
    cog_tools = "<:tool:1254019437854588999>" 
    cog_level = "<:levelup:1367593309345943632>"
    cog_economy = "<:economy:1278762763098783835>"

    pp_cringe = "<:pepe_cringe:1279336502165508148>"

class loging_channels:
    join = 0
    leave = 0
    mail = 0
    count = 0
    error_log = 0
    bot_log = 0

class color:
    no_color = 0x2c2c34

class images:
    weather_thumbnail = "https://i.imgur.com/yro1H4M.png"
