import psutil
import os
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from data.settings.bot_basic_parameters import config
from data.modules.Utilities.autor import autor
from data.modules.Utilities.user import user
from data.modules.utils import core as cr

class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["pomocy"])
    async def help(self, ctx, decyzja="brak"):
        server = self.bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in cr.server_parameters:
            cr.server_parameters[server_id] = cr.GuildParameters(server_id)
        prefix = await cr.server_parameters[server_id].get_prefix()

        version = config.version
        if not decyzja.isdigit():
            decyzja = decyzja.lower()
        if decyzja == "1" or decyzja == "muzyka":
            embed = discord.Embed(
                colour=discord.Colour.blue()
            )

            embed.set_author(name="Sekcja pomocy bota KBot wersja {} (strona 1/5)".format(version))
            embed.add_field(name="{}wkrocz [nazwa kanału]".format(prefix), value="Wkracza z buta na czat głosowy",
                            inline=False)
            embed.add_field(name="{}strumykuj <url>".format(prefix), value="Strumykuj z interneta pieśni",
                            inline=False)
            embed.add_field(name="{}następna".format(prefix), value="Przewiń do kolejnej pieśni",
                            inline=False)
            embed.add_field(name="{}adminnext".format(prefix), value="Pomiń pieśń jak król",
                            inline=False)
            embed.add_field(name="{}pętla".format(prefix), value="Zapętlij pieśń",
                            inline=False)
            embed.add_field(name="{}teraz".format(prefix), value="Wyświetl informacje o aktualnie granej pieśni",
                            inline=False)
            embed.add_field(name="{}kolejka".format(prefix), value="Sprawdź zawartość kolejki",
                            inline=False)
            embed.add_field(name="{}czyść_kolejke".format(prefix), value="Wyczyść kolejkę z niepotrzebnych pieśni",
                            inline=False)
            embed.add_field(name="{}harmider <wartość (od 0 do 150)>".format(prefix), value="Zmienia głośność bota",
                            inline=False)
            embed.add_field(name="{}pauzuj".format(prefix), value="Pauzuje graną pieśń",
                            inline=False)
            embed.add_field(name="{}wznów".format(prefix), value="Wznawia wstrzymaną pieśń",
                            inline=False)
            embed.add_field(name="{}wypad".format(prefix), value="Zatrzymuje bota i rozłącza go z czatem głosowym",
                            inline=False)

            await ctx.send(embed=embed)

        elif decyzja == "2" or decyzja == "ekonomia":
            embed = discord.Embed(
                colour=discord.Colour.blue()
            )

            embed.set_author(name="Sekcja pomocy KBot wersja {} (strona 2/5)".format(version))
            embed.add_field(name="{}przelej <użytkownik> <ilość pieniędzy>".format(prefix),
                            value="Przelej pieniądze komuś", inline=False)
            embed.add_field(name="{}stan_konta [użytkownik]".format(prefix),
                            value="Sprawdź swój lub czyiś stan konta", inline=False)
            embed.add_field(name="{}dodaj_pieniądze <użytkownik> <ilość pieniędzy>".format(prefix),
                            value="Dodrukuj pieniądze", inline=False)
            embed.add_field(name="{}spal_pieniądze <użytkownik> <ilość pieniędzy>".format(prefix),
                            value="Spal nadmiar pieniędzy", inline=False)
            embed.add_field(name="{}reset_ekonomii".format(prefix),
                            value="Reset całej ekonomii", inline=False)
            embed.add_field(name="{}lista_kont".format(prefix),
                            value="Wyświetl listę krezusów", inline=False)

            await ctx.send(embed=embed)

        elif decyzja == "3" or decyzja == "narzędzia":
            embed = discord.Embed(
                colour=discord.Colour.blue()
            )

            embed.set_author(name="Sekcja pomocy KBot wersja {} (strona 3/5)".format(version))
            embed.add_field(name="{}ping".format(prefix), value="Dowiedz się jak słabego mam neta",
                            inline=False)
            embed.add_field(name="{}zaproszenie".format(prefix), value="We no zaproś na serwerek",
                            inline=False)
            embed.add_field(name="{}autor".format(prefix),
                            value="Wpiszta by się dowiedzieć więcej o Stwórcy tego dzieła",
                            inline=False)
            embed.add_field(name="{}info_bot".format(prefix), value="Informacje o mnie",
                            inline=False)
            embed.add_field(name="{}serwer".format(prefix), value="Informacje o serwerze",
                            inline=False)
            embed.add_field(name="{}użytkownik <nick, @nick lub id>".format(prefix),
                            value="Informacje o danym użytkowniku", inline=False)
            embed.add_field(name="{}ustawienia".format(prefix), value="Panel Ustawień",
                            inline=False)

            await ctx.send(embed=embed)

        elif decyzja == "4" or decyzja == "administracja":
            embed = discord.Embed(
                colour=discord.Colour.blue()
            )

            embed.set_author(name="Sekcja pomocy KBot wersja {} (strona 4/5)".format(version))
            embed.add_field(name="{}kopnij".format(prefix), value="Kopnij w tyłek",
                            inline=False)
            embed.add_field(name="{}ukarz".format(prefix), value="Ukarz delikwenta na tułaczkę",
                            inline=False)
            embed.add_field(name="{}wybacz".format(prefix), value="Wybacz mu",
                            inline=False)
            embed.add_field(name="{}skazańcy".format(prefix), value="Lista skazańców",
                            inline=False)
            embed.add_field(name="{}czyść <liczba> [użytkownik]".format(prefix), value="Służba sprzątania czatu",
                            inline=False)
            embed.add_field(name="{}dodaj_role <użytkownik> <rola>".format(prefix), value="Obdaruj użytkownika rolą",
                            inline=False)
            embed.add_field(name="{}usuń_role <użytkownik> <rola>".format(prefix), value="Zabierz nikczemnikowi rolę",
                            inline=False)

            await ctx.send(embed=embed)

        elif decyzja == "5" or decyzja == "rozrywka":
            embed = discord.Embed(
                colour=discord.Colour.blue()
            )

            embed.set_author(name="Sekcja pomocy KBot wersja {} (strona 5/5)".format(version))
            embed.add_field(name="{}kostka <ile ścian (minimum 4)>".format(prefix),
                            value="Weźse wylosuj jakąś liczbunie szefuńciu", inline=False)
            embed.add_field(name="{}zapytaj <pytanie>".format(prefix), value="Zapytaj mnie o cokolwiek",
                            inline=False)
            embed.add_field(name="{}pkn <papier, kamień lub nożyce>".format(prefix),
                            value="Zagraj ze mną w papier, kamień i nożyce", inline=False)
            embed.add_field(name="{}zgadywanka".format(prefix), value="Odgadnij liczbę",
                            inline=False)
            embed.add_field(name="{}moneta".format(prefix), value="Rzuć monetą",
                            inline=False)

            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(
                colour=discord.Colour.blue()
            )

            embed.set_author(name="Sekcja pomocy KBot wersja {} (wprowadzenie)".format(version))
            embed.add_field(name="{}pomocy [kategoria]".format(prefix),
                            value="Kategorie: 1 - Muzyka, 2 - Ekonomia, 3 - Narzędzia, 4 - Administracja, 5 - Rozrywka",
                            inline=False)
            await ctx.send(embed=embed)
            await ctx.send("```"
                           "Możesz używać zarówno liczb jak i nazw kategorii!"
                           "```")

    @commands.command()
    async def author(self, ctx):
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
        embed.add_field(name="Wersja:", value=config.version, inline=False)
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

    @commands.command(aliases=["ustawienia"])
    @has_permissions(administrator=True)
    async def settings(self, ctx, setting: str = None, switch=None):
        """Panel Ustawień"""
        server = self.bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in cr.server_parameters:
            cr.server_parameters[server_id] = cr.GuildParameters(server_id)
        server_config = await cr.server_parameters[server_id].check_config()
        prefix = await cr.server_parameters[server_id].get_prefix()
        if setting is not None:
            setting.lower()

        async def help_menu():
            embed = discord.Embed(
                colour=discord.Colour.blue()
            )

            embed.set_author(name="Ustawienia bota KBot {} na serwerze {}".format(config.version, ctx.guild.name))
            embed.add_field(name="Wymagana rola DJ: {}".format(
                server_config["require_dj"]),
                value="{}settings dj <on/off>".format(prefix), inline=False
            )
            embed.add_field(name="Zapobieganie duplikacji pieśni w kolejce: {}".format(
                server_config["QSP"]),
                value="{}settings QSP <on/off>".format(prefix), inline=False
            )
            embed.add_field(name="Prefix: {}".format(
                prefix),
                value="{}settings prefix <nowy prefix>".format(prefix), inline=False
            )
            embed.add_field(name="Autorola: {}".format(
                server_config["autorole"]),
                value="{}settings autorole <rola do przydzielenia/brak>".format(prefix), inline=False
            )
            embed.add_field(name="Symbol waluty: {}".format(
                server_config["currency_symbol"]),
                value="{}settings curr_symbol <symbol>".format(prefix), inline=False
            )

            await ctx.send(embed=embed)

        if setting is None and switch is None:
            await help_menu()

        elif setting == "dj":
            if switch == "on":
                setting_state = ("require_dj", "on")
                await cr.server_parameters[server_id].change_config(setting_state)
                cr.server_parameters[server_id].require_dj = "on"
                await ctx.send("Wymaganie roli DJ pomyślnie włączone!")
            elif switch == "off":
                setting_state = ("require_dj", "off")
                await cr.server_parameters[server_id].change_config(setting_state)
                cr.server_parameters[server_id].require_dj = "off"
                await ctx.send("Wymaganie roli DJ pomyślnie wyłączone!")
            elif switch is None:
                embed = discord.Embed(
                    colour=discord.Colour.blue()
                )

                embed.set_author(name="Ustawienie parametru")
                embed.add_field(name="Wymagana rola DJ: {}".format(
                                server_config["require_dj"]),
                                value="{}settings dj <on/off>".format(prefix), inline=False)

                await ctx.send(embed=embed)
            else:
                await ctx.send("Nieprawidłowa wartość! Wpisz {}settings, by dowiedzieć się więcej".format(prefix))

        elif setting == "qsp":
            if switch == "on":
                setting_state = ("QSP", True)
                await cr.server_parameters[server_id].change_config(setting_state)
                await ctx.send("Zapobieganie duplikacji pieśni w kolejce pomyślnie włączone!")
            elif switch == "off":
                setting_state = ("QSP", False)
                await cr.server_parameters[server_id].change_config(setting_state)
                await ctx.send("Zapobieganie duplikacji pieśni w kolejce pomyślnie wyłączone!")
            elif switch is None:
                embed = discord.Embed(
                    colour=discord.Colour.blue()
                )

                embed.set_author(name="Ustawienie parametru")
                embed.add_field(name="Zapobieganie duplikacji pieśni w kolejce: {}".format(
                    server_config["QSP"]),
                    value="{}settings QSP <on/off>".format(prefix), inline=False)

                await ctx.send(embed=embed)
            else:
                await ctx.send("Nieprawidłowa wartość! Wpisz {}settings, by dowiedzieć się więcej".format(prefix))

        elif setting == "prefix":
            new_prefix = str(switch)
            if switch == prefix:
                await ctx.send("Już jest ustawiony taki prefix!")
            elif len(switch) > 5:
                await ctx.send("Ten prefix jest za długi! Maksymalna długość prefixu to 5 znaków!")
            elif switch is None:
                embed = discord.Embed(
                    colour=discord.Colour.blue()
                )

                embed.set_author(name="Ustawienie parametru")
                embed.add_field(name="Prefix: {}".format(
                    prefix),
                    value="{}settings prefix <nowy prefix>".format(prefix), inline=False)

                await ctx.send(embed=embed)
            else:
                await cr.server_parameters[server_id].change_prefix(ctx, new_prefix)

        elif setting == "autorole":
            # TODO: Zamiana parametru on na konkretną rolę na serwerze
            if switch == "on":
                setting_state = ("autorole", "on")
                await cr.server_parameters[server_id].change_config(setting_state)
                await ctx.send("Autorola pomyślnie ustawiona!")
            elif switch == "brak":
                setting_state = ("autorole", None)
                await cr.server_parameters[server_id].change_config(setting_state)
                await ctx.send("Autorola pomyślnie wyłączona!")
            elif switch is None:
                embed = discord.Embed(
                    colour=discord.Colour.blue()
                )

                embed.set_author(name="Ustawienie parametru")
                embed.add_field(name="Autorola: {}".format(
                                server_config["autorole"]),
                                value="{}settings autorole <rola do przydzielenia/brak>".format(prefix), inline=False)

                await ctx.send(embed=embed)
            else:
                await ctx.send("Nieprawidłowa wartość! Wpisz {}settings, by dowiedzieć się więcej".format(prefix))

        elif setting == "curr_symbol":
            if switch is not None and len(switch) <= 5:
                setting_state = ("currency_symbol", switch)
                await cr.server_parameters[server_id].change_config(setting_state)
                await ctx.send("Symbol waluty pomyślnie zmieniony!")
            elif switch is None:
                embed = discord.Embed(
                    colour=discord.Colour.blue()
                )

                embed.set_author(name="Ustawienie parametru")
                embed.add_field(name="Symbol waluty: {}".format(
                                server_config["currency_symbol"]),
                                value="{}settings curr_symbol <symbol>".format(prefix), inline=False)

                await ctx.send(embed=embed)
            else:
                # noinspection PyTypeChecker
                if len(switch) > 5:
                    await ctx.send("Symbol jest za długi!")
                else:
                    await ctx.send("Nieprawidłowa wartość! Wpisz {}settings, by dowiedzieć się więcej".format(prefix))

        else:
            await help_menu()

def setup(bot):
    bot.add_cog(Utilities(bot))
