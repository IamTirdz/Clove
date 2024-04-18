import discord

from typing import Union
from discord.ext import commands


def is_owner(ctx) -> bool:
    return ctx.author.id == ctx.bot.config.discord_owner_id

async def check_permissions(ctx, perms, *, check=all) -> bool:
    if ctx.author.id == ctx.bot.config.discord_owner_id:
        return True

    resolved = ctx.channel.permissions_for(ctx.author)
    return check(getattr(resolved, name, None) == value for name, value in perms.items())

def has_permissions(*, check=all, **perms) -> bool:
    async def pred(ctx):
        return await check_permissions(ctx, perms, check=check)
    
    return commands.check(pred)

async def check_priv(ctx, member: discord.Member) -> Union[discord.Message, bool, None]:
    try:
        # Self checks
        if member.id == ctx.author.id:
            return await ctx.send(f"You can't {ctx.command.name} yourself")
        
        if member.id == ctx.bot.user.id:
            return await ctx.send("So that's what you think of me huh..? sad ;-;")

        # Check if user bypasses
        if ctx.author.id == ctx.guild.owner.id:
            return False

        # Permission check
        if member.id == ctx.bot.config.discord_owner_id:
            if ctx.author.id != ctx.bot.config.discord_owner_id:
                return await ctx.send(f"I can't {ctx.command.name} my creator ;-;")
            else:
                pass

        if member.id == ctx.guild.owner.id:
            return await ctx.send(f"You can't {ctx.command.name} the owner, lol")
        
        if ctx.author.top_role == member.top_role:
            return await ctx.send(f"You can't {ctx.command.name} someone who has the same permissions as you...")
        
        if ctx.author.top_role < member.top_role:
            return await ctx.send(f"Nope, you can't {ctx.command.name} someone higher than yourself.")
        
    except Exception:
        pass

def can_handle(ctx, permission: str) -> bool:
    return isinstance(ctx.channel, discord.DMChannel) or \
        getattr(ctx.channel.permissions_for(ctx.guild.me), permission)
