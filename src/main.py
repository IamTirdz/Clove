import discord
from discord.ext import commands
import time
import config

client = commands.Bot(command_prefix = config.PREFIX, intents =  discord.Intents().all())
client.remove_command('help')


@client.event
async def on_ready():
    print("Logged in as {0.user}".format(client))
    print(f"{config.BOT_NAME} is online")
    
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=" to do fun stuff ✨"))

@client.command(name='ping')
async def ping_command(ctx):
    before = time.monotonic()
    before_ws = int(round(client.latency * 1000, 1))
    message = await ctx.send("Pong!")
    ping = int((time.monotonic() - before) * 1000)

    await message.edit(content=f'🏓 WS: {before_ws}ms | REST: {ping}ms')

client.run(config.TOKEN)
