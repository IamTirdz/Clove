import random
import discord
import secrets
import asyncio
import aiohttp

from io import BytesIO
from discord.ext import commands
from utils import permissions, http


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="8ball", description="Consult 8ball to receive an answer.")
    async def eightball(self, ctx, *, question: commands.clean_content):
        ballresponse = [
            "Yes", "No", "Take a wild guess...", "Very doubtful",
            "Sure", "Without a doubt", "Most likely", "Might be possible",
            "You'll be the judge", "no... (╯°□°）╯︵ ┻━┻", "no... baka",
            "senpai, pls no ;-;"
        ]

        answer = random.choice(ballresponse)
        await ctx.send(f"🎱 **Question:** {question}\n**Answer:** {answer}")

    async def randomimageapi(self, ctx, url: str, *endpoint: str) -> discord.Message:
        try:
            r = await http.get(url, res_method="json")
        except aiohttp.ClientConnectorError:
            return await ctx.send("The API seems to be down...")
        except aiohttp.ContentTypeError:
            return await ctx.send("The API returned an error or didn't return JSON...")

        result = r.response
        for step in endpoint:
            result = result[step]

        await ctx.send(result)

    async def api_img_creator(self, ctx, url: str, filename: str, content: str = None) -> discord.Message:
        async with ctx.channel.typing():
            req = await http.get(url, res_method="read")

            if not req.response:
                return await ctx.send("I couldn't create the image ;-;")

            bio = BytesIO(req.response)
            bio.seek(0)

            return await ctx.send(content=content, file=discord.File(bio, filename=filename))

    @commands.command(name="duck", description="Posts a random duck.")
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def duck(self, ctx):
        await self.randomimageapi(ctx, "https://random-d.uk/api/v1/random", "url")

    @commands.command(name="coffee", description="Posts a random coffee.")
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def coffee(self, ctx):
        await self.randomimageapi(ctx, "https://coffee.alexflipnote.dev/random.json", "file")

    @commands.command(name="bird", description="Posts a random bird.")
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def bird(self, ctx):
        await self.randomimageapi(ctx, "https://api.alexflipnote.dev/birb", "file")

    @commands.command(name="sadcat", description="Post a random sadcat.")
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def sadcat(self, ctx):
        await self.randomimageapi(ctx, "https://api.alexflipnote.dev/sadcat", "file")

    @commands.command(name="cat", description="Posts a random cat.")
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def cat(self, ctx):
        await self.randomimageapi(ctx, "https://api.alexflipnote.dev/cats", "file")

    @commands.command(name="dog", description="Posts a random dog.")
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def dog(self, ctx):
        await self.randomimageapi(ctx, "https://api.alexflipnote.dev/dogs", "file")

    @commands.command(aliases=["flip", "coin"], name="coinflip", description="Coinflip!")
    async def coinflip(self, ctx):
        coinsides = ["Heads", "Tails"]
        await ctx.send(f"**{ctx.author.name}** flipped a coin and got **{random.choice(coinsides)}**!")

    @commands.command(name="f", description="Press 'F' to pay respect.")
    async def f(self, ctx, *, text: commands.clean_content = None):
        hearts = ["❤", "💛", "💚", "💙", "💜"]
        reason = f"for **{text}** " if text else ""

        await ctx.send(f"**{ctx.author.name}** has paid their respect {reason}{random.choice(hearts)}")

    @commands.command(name="search", description="Find the 'best' definition to your words.")
    @commands.cooldown(rate=1, per=2.0, type=commands.BucketType.user)
    async def urban(self, ctx, *, search: commands.clean_content):
        async with ctx.channel.typing():
            try:
                r = await http.get(f"https://api.urbandictionary.com/v0/define?term={search}", res_method="json")
            except Exception:
                return await ctx.send("Urban API returned invalid data... might be down atm.")

            if not r.response:
                return await ctx.send("I think the API broke...")
            if not len(r.response["list"]):
                return await ctx.send("Couldn't find your search in the dictionary...")

            result = sorted(r.response["list"], reverse=True, key=lambda g: int(g["thumbs_up"]))[0]

            definition = result["definition"]
            if len(definition) >= 1000:
                definition = definition[:1000]
                definition = definition.rsplit(" ", 1)[0]
                definition += "..."

            await ctx.send(f"📚 Definitions for **{result['word']}**```fix\n{definition}```")

    @commands.command(name="reverse", description="Everything you type after reverse will be reversed.")
    async def reverse(self, ctx, *, text: str):
        t_rev = text[::-1].replace("@", "@\u200B").replace("&", "&\u200B")
        await ctx.send(
            f"🔁 {t_rev}",
            allowed_mentions=discord.AllowedMentions.none()
        )

    @commands.command(name="password", description="Generates a random password string for you.")
    async def password(self, ctx, nbytes: int = 18):
        """
        This returns a random URL-safe text string, containing nbytes random bytes.
        The text is Base64 encoded, so on average each byte results in approximately 1.3 characters.
        """
        if nbytes not in range(3, 1401):
            return await ctx.send("I only accept any numbers between 3-1400")
        
        if hasattr(ctx, "guild") and ctx.guild is not None:
            await ctx.send(f"Sending you a private message with your random generated password **{ctx.author.name}**")

        await ctx.author.send(f"🔑 **Here is your password:**\n{secrets.token_urlsafe(nbytes)}")

    @commands.command(name="rate", description="Rates what you desire.")
    async def rate(self, ctx, *, thing: commands.clean_content):
        rate_amount = random.uniform(0.0, 100.0)
        await ctx.send(f"I'd rate `{thing}` a **{round(rate_amount, 4)} / 100**")

    @commands.command(name="beer", description="Give someone a beer! 🍻")
    async def beer(self, ctx, user: discord.Member = None, *, reason: commands.clean_content = ""):
        if not user or user.id == ctx.author.id:
            return await ctx.send(f"**{ctx.author.name}**: paaaarty!🎉🍺")
        
        if user.id == self.bot.user.id:
            return await ctx.send("*drinks beer with you* 🍻")
        
        if user.bot:
            return await ctx.send(f"I would love to give beer to the bot **{ctx.author.name}**, but I don't think it will respond to you :/")

        beer_offer = f"**{user.name}**, you got a 🍺 offer from **{ctx.author.name}**"
        beer_offer = f"{beer_offer}\n\n**Reason:** {reason}" if reason else beer_offer
        msg = await ctx.send(beer_offer)

        def reaction_check(m):
            if m.message_id == msg.id and m.user_id == user.id and str(m.emoji) == "🍻":
                return True
            
            return False

        try:
            await msg.add_reaction("🍻")
            await self.bot.wait_for("raw_reaction_add", timeout=30.0, check=reaction_check)
            await msg.edit(content=f"**{user.name}** and **{ctx.author.name}** are enjoying a lovely beer together 🍻")
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.send(f"well, doesn't seem like **{user.name}** wanted a beer with you **{ctx.author.name}** ;-;")
        except discord.Forbidden:
            # Bot doesn't have react permission, drop the "offer" word
            beer_offer = f"**{user.name}**, you got a 🍺 from **{ctx.author.name}**"
            beer_offer = f"{beer_offer}\n\n**Reason:** {reason}" if reason else beer_offer
            await msg.edit(content=beer_offer)

    @commands.command(aliases=["howhot", "hot"], name="hotcalc", description="Returns a random percent for how hot is a discord user.")
    async def hotcalc(self, ctx, *, user: discord.Member = None):
        user = user or ctx.author
        random.seed(user.id)
        r = random.randint(1, 100)
        hot = r / 1.17

        if hot > 75:
            emoji = "💞"
        elif hot > 50:
            emoji = "💖"
        elif hot > 25:
            emoji = "❤"
        else:
            emoji = "💔"

        await ctx.send(f"**{user.name}** is **{hot:.2f}%** hot {emoji}")

    @commands.command(aliases=["noticemesenpai"], name="noticeme", description="Notice me senpai! uwu.")
    async def noticeme(self, ctx):
        if not permissions.can_handle(ctx, "attach_files"):
            return await ctx.send("I cannot send images here ;-;")

        r = await http.get("https://i.alexflipnote.dev/500ce4.gif", res_method="read")
        bio = BytesIO(r.response)

        await ctx.send(file=discord.File(bio, filename="noticeme.gif"))

    @commands.command(aliases=["slots", "bet"], name="slot", description="Roll the slot machine.")
    async def slot(self, ctx):
        a, b, c = [random.choice("🍎🍊🍐🍋🍉🍇🍓🍒") for _ in range(3)]

        if (a == b == c):
            results = "All matching, you won! 🎉"
        elif (a == b) or (a == c) or (b == c):
            results = "2 in a row, you won! 🎉"
        else:
            results = "No match, you lost 😢"

        await ctx.send(f"**[ {a} {b} {c} ]\n{ctx.author.name}**, {results}")

    @commands.command(name="dice", description="Dice game. Good luck.")
    async def dice(self, ctx):
        bot_dice, player_dice = [random.randint(1, 6) for g in range(2)]

        results = "\n".join([
            f"**{self.bot.user.display_name}:** 🎲 {bot_dice}",
            f"**{ctx.author.display_name}** 🎲 {player_dice}"
        ])

        if player_dice > bot_dice:
            final_message = "Congrats, you won 🎉"
        if player_dice < bot_dice:
            final_message = "You lost, try again... 🍃"
        else:
            final_message = "It's a tie 🎲"

        await ctx.send(f"{results}\n> {final_message}")

    @commands.command(aliases=["roul", "cg"], name="colorgame", description="Colour game roulette.")
    async def roulette(self, ctx, picked_colour: str = None):
        colour_table = ["blue", "red", "green", "yellow", "black", "white"]
        if not picked_colour:
            pretty_colours = ", ".join(colour_table)
            return await ctx.send(f"Please pick a colour from: {pretty_colours}")

        picked_colour = picked_colour.lower()
        if picked_colour not in colour_table:
            return await ctx.send("Please give correct color")

        chosen_color = random.choice(colour_table)
        msg = await ctx.send("Spinning 🔵🔴🟢🟡⚫⚪")
        await asyncio.sleep(2)
        result = f"Result: {chosen_color.upper()}"

        if chosen_color == picked_colour:
            return await msg.edit(content=f"> {result}\nCongrats, you won 🎉!")
        
        await msg.edit(content=f"> {result}\nBetter luck next time")

async def setup(bot):
    await bot.add_cog(Fun(bot))
