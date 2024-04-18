import discord
import psutil
import os

from datetime import datetime
from discord.ext import commands
from discord.ext.commands import errors
from utils import default, permissions


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.process = psutil.Process(os.getpid())

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if not self.bot.is_ready() or msg.author.bot or \
           not permissions.can_handle(msg, "send_messages"):
            return
        
    async def error_logs(self, ctx, msg, color):
        await self.message_logs(ctx, msg, color, self.bot.config.support_guild_bot_errors, ctx.guild.icon.url)

    async def server_logs(self, ctx, msg):
        support_server = self.bot.get_guild(self.bot.config.support_guild_server)
        guild_name = str(ctx.guild.name).replace(" ", "-").lower()
        channel = discord.utils.get(support_server.channels, name=f"〔📜〕{guild_name}")

        if channel:
            channel_id = channel.id
            await self.message_logs(ctx, msg, discord.Colour.light_gray(), channel_id, ctx.author.avatar.url)
        else:
            if ctx.guild.id == self.bot.config.support_guild_server:
                pass
            else:
                print(f"Error: Server logs channel not found.")
        
    async def message_logs(self, ctx, msg, color, channel, avatar):
        server_channel = self.bot.get_channel(channel)
        server_name = ctx.guild.name if ctx.guild else "Private message"

        embed = discord.Embed(colour=color)
        embed.set_thumbnail(url=avatar)
        embed.add_field(name="Timestamp", value=default.date(datetime.now(), ago=True), inline=False)
        embed.add_field(name="Author", value=str(self.bot.get_user(ctx.author.id)), inline=True)
        embed.add_field(name="Origin", value=server_name, inline=True)
        embed.add_field(name="Message", value=msg, inline=False)

        print(f"[{default.date(datetime.now(), ago=True)}] {server_name} > {str(self.bot.get_user(ctx.author.id))} > {msg}")
        await server_channel.send(embed=embed)

    async def join_leave_server_logs(self, guild, msg, color, channel):
        server_channel = self.bot.get_channel(channel)
        bot_count = 0
        user_count = 0

        for member in guild.members:
            if member.bot:
                bot_count += 1
            else:
                user_count += 1

        embed = discord.Embed(color=color)
        embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name=" ", value=msg, inline=False)
        embed.add_field(name=" ", value=f"**Bots**: {bot_count} {'bot' if bot_count == 1 else 'bots'}", inline=False)
        embed.add_field(name=" ", value=f"**Users**: {user_count} {'user' if user_count == 1 else 'users'}", inline=False)
        embed.set_footer(text=f"(GUILD ID: {guild.id})")

        print(f"[{default.date(datetime.now(), ago=True)}] {msg}")
        await server_channel.send(embed=embed)
        
    @commands.Cog.listener()
    async def on_command_error(self, ctx, err):
        if isinstance(err, commands.MissingPermissions):
            missing_perm_message = "You don't have permission to use this command."
            await self.error_logs(ctx, missing_perm_message, discord.Colour.orange())
            await ctx.send(missing_perm_message)

        elif isinstance(err, discord.Forbidden) and err.code == 50013:
            forbidden_message = "Bot is missing required permissions to perform this action."
            await self.error_logs(ctx, forbidden_message, discord.Colour.orange())
            await ctx.send(forbidden_message)
        
        elif isinstance(err, errors.MissingRequiredArgument) or isinstance(err, errors.BadArgument):
            helper_message = str(ctx.invoked_subcommand) if ctx.invoked_subcommand else str(ctx.command)
            await self.error_logs(ctx, helper_message, discord.Colour.blue())
            await ctx.send_help(helper_message)

        elif isinstance(err, errors.CommandInvokeError):
            error = default.traceback_maker(err.original)

            if "2000 or fewer" in str(err) and len(ctx.message.clean_content) > 1900:                
                invoke_message = "\n".join([
                    "You attempted to make the command display more than 2,000 characters...",
                    "Both error and command will be ignored."])
                await self.error_logs(ctx, invoke_message, discord.Colour.red())
                return await ctx.send(invoke_message)
            
            error_message = f"There was an error processing the command ;-;\n{error}"
            await self.error_logs(ctx, error_message, discord.Colour.red())
            await ctx.send(error_message)

        elif isinstance(err, errors.CheckFailure):
            pass

        elif isinstance(err, errors.MaxConcurrencyReached):
            max_concurrency_message = "You've reached max capacity of command usage at once, please finish the previous one..."
            await self.error_logs(ctx, max_concurrency_message, discord.Colour.blue())
            await ctx.send(max_concurrency_message)

        elif isinstance(err, errors.CommandOnCooldown):
            on_cooldown_message = f"This command is on cooldown... try again in {err.retry_after:.2f} seconds."
            await self.error_logs(ctx, on_cooldown_message, discord.Colour.blue())
            await ctx.send(on_cooldown_message)

        elif isinstance(err, errors.CommandNotFound):
            await self.error_logs(ctx, f"CommandNotFound: {err}", discord.Colour.red())
            await ctx.send(err)

    @commands.Cog.listener() 
    async def on_command(self, ctx):
        await self.server_logs(ctx, ctx.message.clean_content)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        to_send = next((
            chan for chan in guild.text_channels
            if chan.permissions_for(guild.me).send_messages
        ), None)

        if to_send:
            await to_send.send(self.bot.config.bot_join_message)

        support_server = self.bot.get_guild(self.bot.config.support_guild_server)
        if support_server is None:
            print("Support server not found. Make sure to set the correct support server ID.")
            return
        
        category_name = self.bot.config.support_guild_category
        category = discord.utils.get(support_server.categories, name=category_name)
        if category is None:
            print(f"Category '{category_name}' not found in the support server.")
            return

        guild_name = str(guild.name).replace(" ", "-").lower()
        guild_channel_name = f"〔📜〕{guild_name}"
        existing_channel = discord.utils.get(category.channels, name=guild_channel_name)

        join_channel = self.bot.config.support_guild_join
        await self.join_leave_server_logs(guild, f"**{self.bot.config.bot_name}** has joined Guild **{guild.name}** 🎉", discord.Colour.green(), join_channel)
        
        if existing_channel is not None:
            print(f"Channel already created for {guild_channel_name}")
        else:
            if guild.id == self.bot.config.support_guild_server:
                pass
            
            new_channel = await category.create_text_channel(guild_channel_name)
                        
            embed = discord.Embed(color=discord.Colour.orange())
            embed.add_field(name=" ", value=f"🌟 Created this channel to log all used commands.")
            embed.set_footer(text=f"(GUILD ID: {guild.id})")
            await new_channel.send(embed=embed)
        
    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        leave_channel = self.bot.config.support_guild_leave        
        await self.join_leave_server_logs(guild, f"**{self.bot.config.bot_name}** has left Guild **{guild.name}** 😭", discord.Colour.dark_gray(), leave_channel)
            
async def setup(bot):
    await bot.add_cog(Events(bot))
