from discord.ext import commands
import asyncio
import random
from data.modules.Entertainment.pkn import rsp
from data.modules.Entertainment.coin import coin
from data.modules.Entertainment.zapytaj import answers

class Entertainment(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["zgadywanka"])
    async def guess(self, ctx):
        """Odgadnij liczbę"""
        numbers = ("1", "2", "3", "4", "5", "6", "7", "8", "9", "10")

        await ctx.send("Odgadnij liczbę od 1 do 10. Masz tylko 5 sekund.")
        cho = random.choice(numbers)

        try:
            msg = await self.bot.wait_for("message", timeout=5)
            if ctx.author.bot:
                return None
            elif msg.content.startswith(numbers):
                if msg.content == cho:
                    await ctx.send("Zgadłeś")
                else:
                    await ctx.send("Nie zgadłeś. Niestety")
        except asyncio.TimeoutError:
            await ctx.send("Czas minął. To była liczba {}".format(cho))

    @commands.command(aliases=["zapytaj"])
    async def question(self, ctx, *, pytanie):
        """Zapytaj mnie o cokolwiek"""
        odpowiedzi = answers
        await ctx.send("Pytanie: {}\nOdpowiedź: {}".format(pytanie, random.choice(odpowiedzi)))

    @commands.command(aliases=["pkn"])
    async def rsp(self, ctx, hand):
        await rsp(self, ctx, hand)

    @commands.command(aliases=["kostka"])
    async def dice(self, ctx, boki):
        """Weźse wylosuj jakąś liczbunie szefuńciu"""
        b = int(boki)
        if b == 1:
            await ctx.send("No bez jaj")
        elif b == 2:
            await ctx.send("Rzuć se monetą, a nie głowę zawracasz")
        elif b == 3:
            await ctx.send("Widziałeś kiedyś kostkę 3 ścienną?")
        elif b >= 4:
            await ctx.send("Kostka wypluwa {} szefuńciu".format(str(random.randrange(1, b))))

    @commands.command(aliases=["moneta"])
    async def coin(self, ctx):
        """Rzuć monetą"""
        await coin(self, ctx)

def setup(bot):
    bot.add_cog(Entertainment(bot))
