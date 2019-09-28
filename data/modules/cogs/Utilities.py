import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from data.settings.bot_basic_parameters import config
import psutil
import os
from data.modules.Utilities.pomocy import pomocy
from data.modules.Utilities.autor import autor
from data.modules.Utilities.user import user
from data.modules.utils import core as cr

class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["pomocy"])
    async def help(self, ctx, los=1):
        await pomocy(self, ctx, los=los, wersja=config.wersja)

    @commands.command()
    async def autor(self, ctx):
        await autor(self, ctx)

    @commands.command(aliases=["zaproszenie"])
    async def invite(self, ctx):
        """We no zaproś na serwerek"""
        await ctx.send("Proszę szefuńciu, świeżo wydrukowane\n"
                       "https://discordapp.com/oauth2/authorize?client_id=570288534020161538&permissions=3230726&scope=bot"
                       )

    @commands.command()
    async def info_bot(self, ctx):
        """Komenda do sprawdzenia informacji o bocie"""
        process = psutil.Process(os.getpid())
        embed = discord.Embed(
            colour=discord.Colour.blue()
        )

        embed.set_author(name="Informacje o bocie")
        embed.add_field(name="Godność:", value="Nick: KBot#0091, ID: 570288534020161538", inline=False)
        embed.add_field(name="Uruchomiony:", value=config.boot_date, inline=False)
        embed.add_field(name="Pomiar pulsu:", value="{} ms".format(round(self.bot.latency * 1000)), inline=False)
        embed.add_field(name="RAM:", value="{} MB".format(round(process.memory_info().rss / (1024 * 1024))),
                        inline=False)
        embed.add_field(name="Wersja:", value=config.wersja, inline=False)
        embed.add_field(name="Biblioteka", value="discord.py 1.2.3", inline=False)
        embed.add_field(name="Autor:", value="Kicend#2690", inline=False)
        await ctx.send(embed=embed)

    @commands.command(aliases=["serwer"])
    async def guild(self, ctx):
        """Komenda do uzyskania informacji o serwerze"""
        server = self.bot.get_guild(ctx.guild.id)
        roles = [role for role in server.roles]
        embed = discord.Embed(
            colour=discord.Colour.blue()
        )

        embed.set_author(name="Informacje o serwerze")
        embed.set_thumbnail(url=server.icon_url)
        embed.add_field(name="Nazwa serwera:", value=server.name, inline=False)
        embed.add_field(name="ID serwera:", value=server.id, inline=False)
        embed.add_field(name="Dane właściciela:", value="Nick: {}, ID: {}".format(server.owner, server.owner_id),
                        inline=False)
        embed.add_field(name="Role ({}):".format(len(roles)), value="".join([role.mention for role in roles]),
                        inline=False)
        embed.add_field(name="Region serwera:", value=server.region, inline=False)
        embed.add_field(name="Serwer założony:", value=server.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"),
                        inline=False)
        embed.add_field(name="Liczba użytkowników:", value=str(len(server.members)), inline=False)
        embed.set_footer(text="Prośba o dane od {}".format(ctx.author), icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.command()
    async def ping(self, ctx):
        """Dowiedz się jak słabego mam neta"""
        await ctx.send("Pong! {} ms".format(round(self.bot.latency * 1000)))

    @commands.command(aliases=["użytkownik"])
    @has_permissions(manage_messages=True)
    async def user(self, ctx, user_ext_info: discord.Member):
        """Komenda do uzyskiwania informacji o użytkowniku oznaczając go (@nick, nick lub id)"""
        await user(self, ctx, user_ext_info)

    @commands.command(aliases=["zmiana_prefixu"])
    @has_permissions(administrator=True)
    async def change_prefix(self, ctx, prefix: str):
        """Zmiana prefixu bota"""
        server = self.bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in cr.server_parameters:
            cr.server_parameters[server_id] = cr.GuildParameters(server_id)

        await cr.server_parameters[server_id].change_prefix(ctx, prefix)

    @commands.command(aliases=["ustawienia"])
    @has_permissions(administrator=True)
    async def settings(self, ctx, setting=None, switch=None):
        """Panel Ustawień"""
        server = self.bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in cr.server_parameters:
            cr.server_parameters[server_id] = cr.GuildParameters(server_id)
        if setting and switch is None:
            embed = discord.Embed(
                colour=discord.Colour.blue()
            )

            embed.set_author(name="Ustawienia bota Kbot {}".format(config.wersja))
            embed.add_field(name="Wymagana rola DJ: {}".format(
                cr.server_parameters[server_id].config["dj_require"]),
                value="!settings dj <on/off>", inline=False
            )
            embed.add_field(name="Zapobieganie duplikacji pieśni w kolejce: {}".format(
                cr.server_parameters[server_id].config["QSP"]),
                value="!settings QSP <on/off>", inline=False
            )
            embed.add_field(name="Autorola: {}".format(
                cr.server_parameters[server_id].config["autorole"]),
                value="!settings autorole <rola do przydzielenia>", inline=False
            )

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Utilities(bot))
