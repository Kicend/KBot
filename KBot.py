import asyncio
import discord
import youtube_dl
import psutil
import os
import time
from discord.ext import commands
from discord.ext.commands import has_permissions
import random
from itertools import cycle

# Importowanie modułów z folderu data
from data.zapytaj import answers
from data.autor import autor
from data.pomocy import pomocy
from data.pkn import rsp
from data.coin import coin
from data.user import user

# Importowanie konfiguracji bota
from settings.config import Config

# Importowanie polskich komunikatów błędów
from data.lang.pl_PL import error_PL_db

# Listy do przechowywania danych
server_players = {}
users = []

# Parametry bota
wersja = "0.16"
TOKEN = Config.TOKEN
boot_date = time.strftime("%H:%M %d.%m.%Y UTC")

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class Player(object):
    def __init__(self, id):
        self.now = 0
        self.id = id
        self.kolejka = []
        self.piosenki = []
        self.gra = []

    async def main(self, ctx):
        self.task = asyncio.create_task(Player.odtwarzacz(self, ctx))
        await self.task

    async def odtwarzacz(self, ctx):
        while True:
            self.now = 0
            self.gra.append(self.kolejka[0])
            url = self.kolejka.pop(0)
            player = await YTDLSource.from_url(url, loop=False, stream=True)
            ctx.voice_client.play(player, after=lambda e: print('Błąd bota: %s' % e) if e else None)

            await ctx.send('Teraz muzykuję: {}'.format(player.title))
            dictMeta = ytdl.extract_info(url, download=False)
            duration = dictMeta['duration']
            if self.piosenki != []:
                del self.piosenki[0]
            await Player.current_time(self, duration)
            del self.gra[0]
            if self.gra == [] and self.kolejka == []:
                await ctx.send("Odtwarzacz kończy pracę")
                break
        await asyncio.sleep(30)
        if self.gra != [] or self.kolejka != []:
            return None
        else:
            await ctx.voice_client.disconnect()
            await asyncio.sleep(30)
            if self.gra != [] or self.kolejka !=[]:
                return None
            else:
                del server_players[self.id]

    async def konwerter(self, czas):
        minuty = czas / 60
        sekundy = czas % 60
        if sekundy > 9:
            return "{}:{}".format(int(round(minuty - 0.5, 0)), sekundy)
        else:
            return "{}:0{}".format(int(round(minuty - 0.5, 0)), sekundy)

    async def current_time(self, czas):
        while self.now != czas:
            self.now += 1
            await asyncio.sleep(1)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["wkrocz"])
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Wkracza z buta na czat głosowy"""
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command(aliases=["strumykuj"])
    async def play(self, ctx, *, url):
        """Strumykuj z interneta pieśni"""
        server = bot.get_guild(ctx.guild.id)
        server_id = server.id
        if not url.count("https"):
            await ctx.send("Wyszukiwanie muzyki zostało tymczasowo wyłączone. Przyjmowane są tylko adresy URL!")
        else:
            if server_id not in server_players:
                server_players[server_id] = Player(server_id)
            if server_players[server_id].gra == []:
                await ctx.send("Rozpoczynam odtwarzanie")
                server_players[server_id].kolejka.append(url)
                asyncio.run(await server_players[server_id].main(ctx))
            else:
                if url in server_players[server_id].kolejka:
                    await ctx.send("Nie możesz poczekać? Po co druga taka sama piosenka w kolejce?")
                else:
                    server_players[server_id].kolejka.append(url)
                    dictMeta = ytdl.extract_info(url, download=False)
                    title = dictMeta['title']
                    server_players[server_id].piosenki.append(title)
                    await ctx.send("Pieśń dodana do kolejki")

    @commands.command(aliases=["następna"])
    @commands.has_role("DJ")
    async def next(self, ctx):
        """Przewiń do kolejnej pieśni"""
        server = bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in server_players:
            server_players[server_id] = Player(server_id)
        if server_players[server_id].kolejka != []:
            ctx.voice_client.stop()
            await ctx.send("Pieśń została pominięta")
            del server_players[server_id].gra[0]
            server_players[server_id].task.cancel()
            asyncio.run(await server_players[server_id].main(ctx))
        else:
            await ctx.send("Brak pieśni w kolejce")

    @commands.command(aliases=["pętla"])
    async def loop(self, ctx, switch):
        """Zapętlij pieśń"""
        server = bot.get_guild(ctx.guild.id)
        server_id = server.id
        i = 0
        if server_id not in server_players:
            server_players[server_id] = Player(server_id)
        if server_players[server_id].gra == []:
            await ctx.send("Co ty chcesz zapętlić?")
        else:
            i = int(switch)
            ctx.voice_client.stop()
        if i == 1:
            await ctx.send("Pieśń została zapętlona")
            url = server_players[server_id].gra[0]
        while i == 1:
            async with ctx.typing():
                player = await YTDLSource.from_url(url, loop=False, stream=True)
                ctx.voice_client.play(player, after=lambda e: print('Błąd bota: %s' % e) if e else None)

                dictMeta = ytdl.extract_info(url, download=False)
                a = dictMeta['duration']
                await asyncio.sleep(a)

    @commands.command(aliases=["teraz"])
    async def current(self, ctx):
        """Wyświetl informacje o aktualnie granej pieśni"""
        server = bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in server_players:
            server_players[server_id] = Player(server_id)
        if server_players[server_id].gra != []:
            dictMeta = ytdl.extract_info(server_players[server_id].gra[0], download=False)
            czas = dictMeta['duration']

            embed = discord.Embed(
                colour=discord.Colour.blue()
            )

            embed.set_author(name="Aktualnie gra")
            embed.add_field(name="Tytuł:", value=dictMeta['title'], inline=False)
            embed.add_field(name="URL:", value=server_players[server_id].gra[0], inline=False)
            embed.add_field(name="Czas:", value="{}/{}".format(str(await server_players[server_id].konwerter(server_players[server_id].now)), str(await server_players[server_id].konwerter(czas))), inline=False)

            await ctx.send(embed=embed)
        else:
            await ctx.send("Nic nie gra, nie słychać?")

    @commands.command(aliases=["stopuj"])
    async def stop(self, ctx):
        """Stopuje aktualnie graną pieśń"""
        ctx.voice_client.stop()

    @commands.command(aliases=["harmider"])
    async def volume(self, ctx, volume: int):
        """Zmienia głośność bota"""
        if volume > 150:
            await ctx.send("Zgłupiałeś, chcesz ogłuchnąć!?")
        else:
            if ctx.voice_client is None:
                return await ctx.send("Nie jest połączony z żadnym czatem głosowym")

            ctx.voice_client.source.volume = volume / 100
            await ctx.send("Głośność zmieniona na {}%".format(volume))

    @commands.command(aliases=["wypad"])
    async def leave(self, ctx):
        """Zatrzymuje bota i rozłącza go z czatem głosowym"""
        server = bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in server_players:
            server_players[server_id] = Player(server_id)
        await ctx.voice_client.disconnect()
        if server_players[server_id].kolejka != []:
            while server_players[server_id].kolejka != []:
                del server_players[server_id].kolejka[0]
        if server_players[server_id].piosenki != []:
            while server_players[server_id].piosenki != []:
                del server_players[server_id].piosenki[0]
        del server_players[server_id].gra[0]
        del server_players[server_id]
        await ctx.send("Pamięć podręczna została wyczyszczona")

    @commands.command(aliases=["czyść"])
    async def delete_queue(self, ctx):
        """Wyczyść kolejkę z niepotrzebnych pieśni"""
        server = bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in server_players:
            server_players[server_id] = Player(server_id)
        while server_players[server_id].kolejka != []:
            del server_players[server_id].kolejka[0]
        while server_players[server_id].piosenki != []:
            del server_players[server_id].piosenki[0]
        await ctx.send("Kolejka została wyczyszczona z pieśni")

    @commands.command(aliases=["kolejka"])
    async def queue(self, ctx):
        """Sprawdź zawartość kolejki"""
        server = bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in server_players:
            server_players[server_id] = Player(server_id)
        embed = discord.Embed(
            colour=discord.Colour.blue()
        )

        embed.set_author(name="Kolejka bota KBot")

        for liczba, piosenka in enumerate(server_players[server_id].piosenki):
            embed.add_field(name="{} - {}".format(liczba+1, piosenka), value="Piosenka nr {}".format(liczba+1), inline=False)
        if server_players[server_id].piosenki == []:
            await ctx.send("Kolejka jest pusta")
        else:
            await ctx.send(embed=embed)

    #@commands.command()
    #async def konfiguruj(self, ctx, nazwa: str):
        #"""Zaawansowana konfiguracja bota (niezalecane dla początkujących)"""
        #role = discord.utils.get(ctx.guild.roles, name=nazwa)
        #user = ctx.message.author
        #await user.add_roles(role) Przyznawanie roli za pomocą komendy

    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("Nie jesteś związany z żadnym czatem głosowym")
                raise commands.CommandError("Błąd, wleź na jakiś kanał głosowy")

class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["pomocy"])
    async def help(self, ctx, los=1):
        await pomocy(self, ctx, los=los, wersja=wersja)

    @commands.command()
    async def autor(self, ctx):
        await autor(self, ctx)

    @commands.command(aliases=["zaproszenie"])
    async def invite(self, ctx):
        """We no zaproś na serwerek"""
        await ctx.send("Proszę szefuńciu, świeżo wydrukowane\n"
                       "https://discordapp.com/oauth2/authorize?client_id=570288534020161538&permissions=3230726&scope=bot")

    @commands.command()
    async def info_bot(self, ctx):
        """Komenda do sprawdzenia informacji o bocie"""
        process = psutil.Process(os.getpid())
        embed = discord.Embed(
            colour=discord.Colour.blue()
        )

        embed.set_author(name="Informacje o bocie")
        embed.add_field(name="Godność:", value="Nick: KBot#0091, ID: 570288534020161538", inline=False)
        embed.add_field(name="Uruchomiony:", value=boot_date, inline=False)
        embed.add_field(name="Pomiar pulsu:", value="{} ms".format(round(bot.latency * 1000)), inline=False)
        embed.add_field(name="RAM:", value="{} MB".format(round(process.memory_info().rss / (1024 * 1024))),
                        inline=False)
        embed.add_field(name="Wersja:", value=wersja, inline=False)
        embed.add_field(name="Biblioteka", value="discord.py 1.2.3", inline=False)
        embed.add_field(name="Autor:", value="Kicend#2690", inline=False)
        await ctx.send(embed=embed)

    @commands.command(aliases=["serwer"])
    async def guild(self, ctx):
        """Komenda do uzyskania informacji o serwerze"""
        server = bot.get_guild(ctx.guild.id)
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
        await ctx.send("Pong! {} ms".format(round(bot.latency * 1000)))

    @commands.command(aliases=["użytkownik"])
    @has_permissions(manage_messages=True)
    async def user(self, ctx, user_ext_info: discord.Member):
        "Komenda do uzyskiwania informacji o użytkowniku oznaczając go (@nick, nick lub id)"
        await user(self, ctx, user_ext_info)

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
        await member.ban(reason=reason)
        await ctx.send("Użyszkodnik został skazany na tułaczkę\nPowód: {}".format(reason))

    @commands.command(aliases=["wybacz"])
    @has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        """Wybacz mu"""
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split("#")

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send("{} został odbanowany".format(user.mention))
                return

    @commands.command(aliases=["skazańcy"])
    @has_permissions(manage_guild=True)
    async def banlist(self, ctx):
        """Lista skazańców"""
        banned_users = await ctx.guild.bans()

        for ban_entry in banned_users:
            user = ban_entry.user
            if user in users:
                print(None)
            else:
                users.append(user)

        embed = discord.Embed(
            colour=discord.Colour.blue()
        )

        embed.set_author(name="Lista skazanych")

        if users != []:
            for liczba, user in enumerate(users):
                liczba = liczba + 1
                embed.add_field(name="Skazany nr {}".format(liczba), value=user, inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send("Lista skazanych jest pusta")

    @commands.command()
    @has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int, member: discord.Member = None):
        "Komenda do czyszczenia historii czatu"
        deleted = await ctx.channel.purge(limit=amount, check=member)
        if len(deleted) == 1:
            await ctx.send("Usunięto {} wiadomość".format(len(deleted)))
        else:
            await ctx.send("Usunięto {} wiadomości".format(len(deleted)))

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
            msg = await bot.wait_for("message", timeout=5)
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
        "Rzuć monetą"
        await coin(self, ctx)

bot = commands.Bot(command_prefix=commands.when_mentioned_or(Config.commands_prefix),
                   description='KBot wersja {}'.format(wersja))

bot.remove_command("help")

status = ["KBot {}".format(wersja), "!pomocy <1-4>"]

@bot.event
async def on_connect():
    print("Bot pomyślnie połączył się z Discordem\nTrwa wczytywanie danych...")

@bot.event
async def on_ready():
    print('Zalogowany jako {0} ({0.id})'.format(bot.user))
    print('----------------------------------------------')
    msgs = cycle(status)
    while not bot.is_closed():
        current_status = next(msgs)
        game = discord.Game(current_status)
        await bot.change_presence(status=discord.Status.online, activity=game)
        await asyncio.sleep(5)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Nie podałeś wymaganego argumentu")
    elif isinstance(error, commands.CommandInvokeError):
        original = error.original
        if isinstance(original, discord.Forbidden):
            await ctx.send("Nie masz uprawnień do wykonania tej komendy lub Nie mam uprawnień do wykonania tej komendy")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("Nie posiadam takiej komendy w swojej bazie danych")
    elif isinstance(error, commands.CommandError):
        error_content = error.args[0]
        if error_content.count("Role") and error_content.count("required"):
            error = error_PL_db.errors_PL.get(0)
        await ctx.send(error)

bot.add_cog(Music(bot))
bot.add_cog(Utilities(bot))
bot.add_cog(Administration(bot))
bot.add_cog(Entertainment(bot))
bot.run(TOKEN)