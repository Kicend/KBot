import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from data.modules.utils import core as cr
from data.settings.bot_basic_parameters import config

class Administration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["kopnij"])
    @has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="Brak"):
        """Kopnij w tyłek"""
        await member.kick(reason=reason)
        await ctx.send("Użyszkodnik został kopnięty\nPowód: {}".format(reason))

    @commands.command(aliases=["ukarz"])
    @has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="Brak"):
        """Ukarz delikwenta na tułaczkę"""
        server = self.bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in cr.server_tools:
            cr.server_tools[server_id] = cr.Tools(server_id)

        await cr.server_tools[server_id].ban(ctx, member, reason)

    @commands.command(aliases=["wybacz"])
    @has_permissions(ban_members=True)
    async def unban(self, ctx, *, members):
        """Wybacz mu"""
        server = self.bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in cr.server_tools:
            cr.server_tools[server_id] = cr.Tools(server_id)

        await cr.server_tools[server_id].unban(ctx, members)

    @commands.command(aliases=["skazańcy"])
    @has_permissions(manage_guild=True)
    async def banlist(self, ctx):
        """Lista skazańców"""
        server = self.bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in cr.server_tools:
            cr.server_tools[server_id] = cr.Tools(server_id)

        await cr.server_tools[server_id].banlist_display(ctx)

    @commands.command()
    @has_permissions(manage_messages=True)
    async def clear(self, ctx, amount, member: discord.Member = None):
        """Komenda do czyszczenia historii czatu"""
        if amount.isdigit():
            int(amount)
            deleted = await ctx.channel.purge(limit=amount, check=member)
            if len(deleted) == 1:
                await ctx.send("Usunięto {} wiadomość".format(len(deleted)))
            else:
                await ctx.send("Usunięto {} wiadomości".format(len(deleted)))
        elif amount == "all":
            await ctx.channel.purge(check=member)
            await ctx.send("Usunięto wszystkie wiadomości")
        else:
            await ctx.send("Nieprawidłowa wartość argumentu")

    @commands.command(aliases=["dodaj_role"])
    @has_permissions(manage_roles=True)
    async def add_role(self, ctx, member: discord.Member, rola: discord.Role):
        """Obdaruj użytkownika rolą"""
        role_name = rola.name
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        await member.add_roles(role)
        await ctx.send("Rola została przyznana!")

    @commands.command(aliases=["usuń_role"])
    @has_permissions(manage_roles=True)
    async def remove_role(self, ctx, member: discord.Member, rola: discord.Role):
        """Zabierz nikczemnikowi rolę"""
        role_name = rola.name
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        await member.remove_roles(role)
        await ctx.send("Rola została odebrana!")

def setup(bot):
    bot.add_cog(Administration(bot))
