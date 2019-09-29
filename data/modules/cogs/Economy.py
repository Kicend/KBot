import discord
from discord.ext import commands
from discord.ext.commands import has_permissions

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["przelej"])
    async def pay(self, user: discord.Member, amount):
        return True
