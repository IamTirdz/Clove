import aiohttp
import discord
import importlib
import os

from discord.ext import commands
from utils import permissions, default, http


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name="load", description="Loads an extension.")
    @commands.check(permissions.is_owner)
    async def load(self, ctx, name: str):
        try:          
            await self.bot.load_extension(f"cogs.{name}")
        except Exception as e:
            return await ctx.send(default.traceback_maker(e))
        
        await ctx.send(f"Loaded extension **{name}.py**")

    @commands.command(name="unload", description="Unloads an extension.")
    @commands.check(permissions.is_owner)
    async def unload(self, ctx, name: str):
        try:
            await self.bot.unload_extension(f"cogs.{name}")
        except Exception as e:
            return await ctx.send(default.traceback_maker(e))
        
        await ctx.send(f"Unloaded extension **{name}.py**")

    @commands.command(name="reload", description="Reloads an extension.")
    @commands.check(permissions.is_owner)
    async def reload(self, ctx, name: str):
        try:
            await self.bot.reload_extension(f"cogs.{name}")
        except Exception as e:
            return await ctx.send(default.traceback_maker(e))
        
        await ctx.send(f"Reloaded extension **{name}.py**")

    @commands.command(name="realoadall", description="Reloads all extension.")
    @commands.check(permissions.is_owner)
    async def reloadall(self, ctx):
        error_collection = []
        for file in os.listdir("cogs"):
            if not file.endswith(".py"):
                continue

            name = file[:-3]
            try:
                await self.bot.reload_extension(f"cogs.{name}")
            except Exception as e:
                error_collection.append(
                    [file, default.traceback_maker(e, advance=False)]
                )

        if error_collection:
            output = "\n".join([
                f"**{g[0]}** ```diff\n- {g[1]}```"
                for g in error_collection
            ])

            return await ctx.send(
                f"Attempted to reload all extensions, was able to reload, "
                f"however the following failed...\n\n{output}"
            )

        await ctx.send("Successfully reloaded all extensions")

    @commands.command(name="reloadutils", description="Reloads a utils module.")
    @commands.check(permissions.is_owner)
    async def reloadutils(self, ctx, name: str):
        utils_name = f"utils/{name}.py"

        try:
            module_name = importlib.import_module(f"utils.{name}")
            importlib.reload(module_name)
        except ModuleNotFoundError:
            return await ctx.send(f"Couldn't find module named **{utils_name}**")
        except Exception as e:
            error = default.traceback_maker(e)
            return await ctx.send(f"Module **{utils_name}** returned error and was not reloaded...\n{error}")
        
        await ctx.send(f"Reloaded module **{utils_name}**")

    @commands.command(name="dm", description="DM for specific user.")
    @commands.check(permissions.is_owner)
    async def dm(self, ctx, user: discord.User, *, message: str):
        try:
            await user.send(message)
            await ctx.send(f"✉️ Sent a DM to **{user}**")
        except discord.Forbidden:
            await ctx.send("This user might be having DMs blocked or it's a bot account...")

    @commands.group(name="change", description=f"Commands to change bot username, nickname and avatar.")
    @commands.check(permissions.is_owner)
    async def change(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(str(ctx.command))

    @change.command(name="username", description="Change username.")
    @commands.check(permissions.is_owner)
    async def change_username(self, ctx, *, name: str):
        try:
            await self.bot.user.edit(username=name)
            await ctx.send(f"Successfully changed username to **{name}**")
        except discord.HTTPException as err:
            await ctx.send(err)

    @change.command(name="nickname", description="Change nickname.")
    @commands.check(permissions.is_owner)
    async def change_nickname(self, ctx, *, name: str = None):
        try:
            await ctx.guild.me.edit(nick=name)

            if name:
                return await ctx.send(f"Successfully changed nickname to **{name}**")
            
            await ctx.send("Successfully removed nickname")
        except Exception as err:
            await ctx.send(err)

    @change.command(name="avatar", description="Change avatar.")
    @commands.check(permissions.is_owner)
    async def change_avatar(self, ctx, url: str = None):
        if url is None and len(ctx.message.attachments) == 1:
            url = ctx.message.attachments[0].url
        else:
            url = url.strip("<>") if url else None

        try:
            bio = await http.get(url, res_method="read")
            await self.bot.user.edit(avatar=bio.response)
            await ctx.send(f"Successfully changed the avatar. Currently using:\n{url}")
        except aiohttp.InvalidURL:
            await ctx.send("The URL is invalid...")
        except discord.InvalidArgument:
            await ctx.send("This URL does not contain a useable image")
        except discord.HTTPException as err:
            await ctx.send(err)
        except TypeError:
            await ctx.send("You need to either provide an image URL or upload one with the command")

async def setup(bot):
    await bot.add_cog(Admin(bot))
