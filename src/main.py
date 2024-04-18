import discord
from discord.ext import commands
import os

from datetime import datetime
from utils import config


intents = discord.Intents().all()
config = config.Config.from_env(".env")

client = commands.Bot(command_prefix = config.bot_prefix, intents = intents)
client.remove_command('help')

@client.event
async def on_ready():
    if not hasattr(client, "uptime"):
        client.uptime = datetime.now()

    if not hasattr(client, "config"):
        client.config = config

    for file in os.listdir("cogs"):
        if not file.endswith(".py"):
            continue

        name = file[:-3]
        await client.load_extension(f"cogs.{name}")
    
    status = config.bot_status_type
    status_type = {"idle": discord.Status.idle, "dnd": discord.Status.dnd}
    activity = config.bot_activity_type
    activity_type = {"listening": 2, "watching": 3, "competing": 5}

    await client.change_presence(
        activity = discord.Game(type = activity_type.get(activity, 0), name = config.bot_activity_name),
        status = status_type.get(status, discord.Status.online)
    )

    print("Logged in as {0.user}".format(client))
    print(f"{config.bot_name} is now online")
    print("Joined Servers:")
    for guild in client.guilds:
        print(f"- {guild.name} (ID: {guild.id})")
        
    print(f"Ready: {client.user} | Servers: {len(client.guilds)}\n")
    
try:
    client.run(config.bot_token)  
except Exception as e:
    print(f"Error when logging in {config.bot_name} bot")
