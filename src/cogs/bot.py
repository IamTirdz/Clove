import time
import discord
import psutil
import os

from discord.ext import commands
from utils import default


class Bot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.process = psutil.Process(os.getpid())
        
    @commands.command(name="ping", description=f"Ping the bot.")
    async def ping(self, ctx):
        before = time.monotonic()
        before_ws = int(round(self.bot.latency * 1000, 1))
        message = await ctx.send("Pong!")
        ping = int((time.monotonic() - before) * 1000)
        await message.edit(content=f'🏓 WS: {before_ws}ms | REST: {ping}ms')
        
    @commands.command(aliases=["joinme", "join"], name="botinvite", description=f"Invite bot to your server.")
    async def botinvite(self, ctx):
        await ctx.send("\n".join([
            f"**{ctx.author.name}**, use this URL to invite me",
            f"<{discord.utils.oauth_url(self.bot.user.id)}>"
        ]))

    @commands.command(aliases=["supportserver", "feedbackserver"], name="botserver", description="Get an invite to our support server.")
    async def botserver(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel) or ctx.guild.id != self.bot.config.support_guild_server:
            return await ctx.send(f"**Here you go {ctx.author.name} 🍻**\nself.bot.config.support_guild_invite")
        
        await ctx.send(f"**{ctx.author.name}** this is my home you know :3")

    @commands.command(aliases=["info", "stats", "status"], name="about", description=f"About the bot.")
    async def about(self, ctx):
        ramUsage = self.process.memory_full_info().rss / 1024**2
        avgmembers = sum(g.member_count for g in self.bot.guilds) / len(self.bot.guilds)

        embedColour = None
        if hasattr(ctx, "guild") and ctx.guild is not None:
            embedColour = ctx.me.top_role.colour

        embed = discord.Embed(colour=embedColour)
        embed.set_thumbnail(url=ctx.bot.user.avatar)
        embed.add_field(name="Last boot", value=default.date(self.bot.uptime, ago=True))
        embed.add_field(name="Developer", value=str(self.bot.get_user(self.bot.config.bot_owner)))
        embed.add_field(name="Library", value="discord.py")
        embed.add_field(name="Servers", value=f"{len(ctx.bot.guilds)} ( avg: {avgmembers:,.2f} users/server )")
        embed.add_field(name="Commands loaded", value=len([x.name for x in self.bot.commands]))
        embed.add_field(name="RAM", value=f"{ramUsage:.2f} MB")

        await ctx.send(content=f"👨‍💻 About **{ctx.bot.user}**", embed=embed)

    @commands.hybrid_command(name="help", description=f"List of all commands that bot has loaded.")
    async def help(self, ctx):
        embed = discord.Embed(title="Help", description=f"CommandPrefix: '**{self.bot.config.bot_prefix}**'\nList of available commands:", color=0xBEBEFE)
        
        #for cog_name, cog in self.bot.cogs.items():
        for cog_name, cog in [(cog_name, cog) for cog_name, cog in self.bot.cogs.items() if cog_name != "events"]:
            commands = cog.get_commands()
            data = []

            if cog_name.lower() == "owner":
                is_owner = await self.bot.is_owner(ctx.author)
                commands = [cmd for cmd in commands if is_owner or not cmd.name.startswith("owner_")]
            
            for command in commands:
                if command.name.startswith("admin_") and ctx.author.has_permissions(manage_guild=True) and ctx.author.role in self.admin_role:
                    continue

                description = command.description.partition("\n")[0]
                data.append(f"{command.name} - {description}")

            help_text = "\n".join(data)
            embed.add_field(name=cog_name.capitalize(), value=f"`{help_text}`", inline=False)

        await ctx.send(embed=embed)
                
async def setup(bot):
    await bot.add_cog(Bot(bot))
