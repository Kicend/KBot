import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from data.settings.bot_basic_parameters import config
import psutil
import os
from data.modules.Utilities.autor import autor
from data.modules.Utilities.user import user
from data.modules.utils import core as cr

class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["pomocy"])
    async def help(self, ctx, los=1):
        wersja = config.wersja
        decyzja = int(los)
        if decyzja == 1:
            embed = discord.Embed(
                colour=discord.Colour.blue()
            )

            embed.set_author(name="Sekcja pomocy bota KBot wersja {} (strona 1/4)".format(wersja))
            embed.add_field(name="!wkrocz [nazwa kanału]", value="Wkracza z buta na czat głosowy", inline=False)
            embed.add_field(name="!strumykuj <url>", value="Strumykuj z interneta pieśni", inline=False)
            embed.add_field(name="!następna", value="Przewiń do kolejnej pieśni", inline=False)
            embed.add_field(name="!adminnext", value="Pomiń pieśń jak król", inline=False)
            embed.add_field(name="!pętla", value="Zapętlij pieśń", inline=False)
            embed.add_field(name="!teraz", value="Wyświetl informacje o aktualnie granej pieśni", inline=False)
            embed.add_field(name="!kolejka", value="Sprawdź zawartość kolejki", inline=False)
            embed.add_field(name="!czyść_kolejke", value="Wyczyść kolejkę z niepotrzebnych pieśni", inline=False)
            embed.add_field(name="!harmider <wartość (od 0 do 150)>", value="Zmienia głośność bota", inline=False)
            embed.add_field(name="!pauzuj", value="Pauzuje graną pieśń", inline=False)
            embed.add_field(name="!wznów", value="Wznawia wstrzymaną pieśń", inline=False)
            embed.add_field(name="!wypad", value="Zatrzymuje bota i rozłącza go z czatem głosowym", inline=False)

            await ctx.send(embed=embed)

        elif decyzja == 2:
            embed = discord.Embed(
                colour=discord.Colour.blue()
            )

            embed.set_author(name="Sekcja pomocy KBot wersja {} (strona 2/4)".format(wersja))
            embed.add_field(name="!ping", value="Dowiedz się jak słabego mam neta", inline=False)
            embed.add_field(name="!zaproszenie", value="We no zaproś na serwerek", inline=False)
            embed.add_field(name="!autor", value="Wpiszta by się dowiedzieć więcej o Stwórcy tego dzieła", inline=False)
            embed.add_field(name="!info_bot", value="Informacje o mnie", inline=False)
            embed.add_field(name="!serwer", value="Informacje o serwerze", inline=False)
            embed.add_field(name="!użytkownik <nick, @nick lub id>", value="Informacje o danym użytkowniku",
                            inline=False)
            embed.add_field(name="!zmiana_prefixu <nowy prefix>", value="Zmiana prefixu bota", inline=False)
            embed.add_field(name="!ustawienia", value="Panel Ustawień", inline=False)

            await ctx.send(embed=embed)

        elif decyzja == 3:
            embed = discord.Embed(
                colour=discord.Colour.blue()
            )

            embed.set_author(name="Sekcja pomocy KBot wersja {} (strona 3/4)".format(wersja))
            embed.add_field(name="!kopnij", value="Kopnij w tyłek", inline=False)
            embed.add_field(name="!ukarz", value="Ukarz delikwenta na tułaczkę", inline=False)
            embed.add_field(name="!wybacz", value="Wybacz mu", inline=False)
            embed.add_field(name="!skazańcy", value="Lista skazańców", inline=False)
            embed.add_field(name="!czyść <liczba> [użytkownik]", value="Służba sprzątania czatu", inline=False)
            embed.add_field(name="!dodaj_role <użytkownik> <rola>", value="Obdaruj użytkownika rolą", inline=False)
            embed.add_field(name="!usuń_role <użytkownik> <rola>", value="Zabierz nikczemnikowi rolę", inline=False)

            await ctx.send(embed=embed)

        elif decyzja == 4:
            embed = discord.Embed(
                colour=discord.Colour.blue()
            )

            embed.set_author(name="Sekcja pomocy KBot wersja {} (strona 4/4)".format(wersja))
            embed.add_field(name="!kostka <ile ścian (minimum 4)>", value="Weźse wylosuj jakąś liczbunie szefuńciu",
                            inline=False)
            embed.add_field(name="!zapytaj <pytanie>", value="Zapytaj mnie o cokolwiek", inline=False)
            embed.add_field(name="!pkn <papier, kamień lub nożyce>", value="Zagraj ze mną w papier, kamień i nożyce",
                            inline=False)
            embed.add_field(name="!zgadywanka", value="Odgadnij liczbę", inline=False)
            embed.add_field(name="!moneta", value="Rzuć monetą", inline=False)

            await ctx.send(embed=embed)

    @commands.command()
    async def autor(self, ctx):
        await autor(ctx)

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
        await user(ctx, user_ext_info)

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
        server_config = await cr.server_parameters[server_id].config
        if setting is None and switch is None:
            embed = discord.Embed(
                colour=discord.Colour.blue()
            )

            embed.set_author(name="Ustawienia bota KBot {}".format(config.wersja))
            embed.add_field(name="Wymagana rola DJ: {}".format(
                server_config["require_dj"]),
                value="!settings dj <on/off>", inline=False
            )
            embed.add_field(name="Zapobieganie duplikacji pieśni w kolejce: {}".format(
                server_config["QSP"]),
                value="!settings QSP <on/off>", inline=False
            )
            embed.add_field(name="Autorola: {}".format(
                server_config["autorole"]),
                value="!settings autorole <rola do przydzielenia>", inline=False
            )
            embed.add_field(name="Symbol waluty: {}".format(
                server_config["currency_symbol"]),
                value="!settings curr_symbol <symbol>", inline=False
            )

            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Utilities(bot))
