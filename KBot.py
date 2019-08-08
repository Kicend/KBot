import asyncio
import discord
import youtube_dl
from discord.ext import commands
from discord.ext.commands import has_permissions
import random
from random import randrange
from itertools import cycle

# Importowanie modułów z folderu data
from data.zapytaj import a
from data.autor import autor
from data.pomocy import pomocy
from data.pkn import rsp

# Listy do przechowywania danych
kolejka = []
piosenki = []
gra = []
users = []

wersja = "0.10-3"
TOKEN = 'NTcwMjg4NTM0MDIwMTYxNTM4.XL9qbA.z2aE8-wAdad78ox3Dt-N8oswTVA'

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

async def odtwarzacz(ctx):
    while True:
        gra.append(kolejka[0])
        url = kolejka.pop(0)
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=False, stream=True)
            ctx.voice_client.play(player, after=lambda e: print('Błąd bota: %s' % e) if e else None)

            await ctx.send('Teraz muzykuję: {}'.format(player.title))
            piosenki.append(player.title)
            dictMeta = ytdl.extract_info(url, download=False)
            a = dictMeta['duration']
            del piosenki[0]
            await asyncio.sleep(a)
            del gra[0]
            if gra == [] and kolejka == []:
                await ctx.send("Odtwarzacz kończy pracę")
                break
    await asyncio.sleep(30)
    await ctx.voice_client.disconnect()

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
        if gra == []:
            await ctx.send("Rozpoczynam odtwarzanie")
            kolejka.append(url)
            await odtwarzacz(ctx)
        else:
            kolejka.append(url)
            dictMeta = ytdl.extract_info(url, download=False)
            title = dictMeta['title']
            piosenki.append(title)
            await ctx.send("Pieśń dodana do kolejki")

    @commands.command(aliases=["następna"])
    async def next(self, ctx):
        """Przewiń do kolejnej pieśni"""
        if kolejka != []:
            ctx.voice_client.stop()
            await ctx.send("Pieśń została pominięta")
            del gra[0]
            await odtwarzacz(ctx)
        else:
            await ctx.send("Brak pieśni w kolejce")

    @commands.command(aliases=["pętla"])
    async def loop(self, ctx, switch):
        """Zapętlij pieśń"""
        i = int(switch)
        ctx.voice_client.stop()
        if i == 1:
            await ctx.send("Pieśń została zapętlona")
            url = gra[0]
        while i == 1:
            async with ctx.typing():
                player = await YTDLSource.from_url(url, loop=False, stream=True)
                ctx.voice_client.play(player, after=lambda e: print('Błąd bota: %s' % e) if e else None)

                dictMeta = ytdl.extract_info(url, download=False)
                a = dictMeta['duration']
                await asyncio.sleep(a)

    @commands.command(aliases=["teraz"])
    async def info(self, ctx):
        """Wyświetl informacje o aktualnie granej pieśni"""
        if gra != []:
            await ctx.send("Aktualnie gra {}".format(gra[0]))
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
        await ctx.voice_client.disconnect()
        if kolejka != []:
            while kolejka != []:
                del kolejka[0]
        if piosenki != []:
            while piosenki != []:
                del piosenki[0]
        del gra[0]
        await ctx.send("Pamięć podręczna została wyczyszczona")

    @commands.command(aliases=["czyść"])
    async def delete_queue(self, ctx):
        """Wyczyśc kolejkę z niepotrzebnych pieśni"""
        while kolejka != []:
            del kolejka[0]
        while piosenki != []:
            del piosenki[0]
        await ctx.send("Kolejka została wyczyszczona z pieśni")

    @commands.command(aliases=["kolejka"])
    async def queue(self, ctx):
        """Sprawdź zawartość kolejki"""
        embed = discord.Embed(
            colour=discord.Colour.blue()
        )

        embed.set_author(name="Kolejka bota KBot")

        for liczba, piosenka in enumerate(piosenki):
            embed.add_field(name="{} - {}".format(liczba, piosenka), value="Piosenka nr {}".format(liczba), inline=False)
        if piosenki == []:
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
    async def ping(self, ctx):
        """Dowiedz się jak słabego mam neta"""
        await ctx.send("Pong! {} ms".format(round(bot.latency * 1000)))

    @commands.command(aliases=["zapytaj"])
    async def question(self, ctx, *, pytanie):
        """Zapytaj mnie o cokolwiek"""
        odpowiedzi = a
        await ctx.send("Pytanie: {}\nOdpowiedź: {}".format(pytanie, random.choice(odpowiedzi)))

    @commands.command(aliases=["pkn"])
    async def rsp(self, ctx, hand):
        await rsp(self, ctx, hand)

    @commands.command(aliases=["kostka"])
    async def dice(self, ctx, boki):
        """Weźse wylosuj jakąś liczbunie szefuńciu"""
        b = int(boki)
        if b == 3:
            await ctx.send("Widziałeś kiedyś kostkę 3 ścienną?")

        if b == 2:
            await ctx.send("Rzuć se monetą, a nie głowę zawracasz")

        if b == 1:
            await ctx.send("No bez jaj")

        if b >= 4:
            a = str(randrange(1, b))

            await ctx.send("Kostka wypluwa {} szefuńciu".format(a))

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

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"),
                   description='KBot wersja {}'.format(wersja))

bot.remove_command("help")

status = ["KBot {}".format(wersja), "!pomocy <1-3>"]

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
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Nie masz uprawnień do wykonania tej komendy")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Nie podałeś wymaganego argumentu")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.BotMissingPermissions):
        await ctx.send("Nie mam uprawnień do wykonania tej komendy")

bot.add_cog(Music(bot))
bot.add_cog(Utilities(bot))
bot.add_cog(Administration(bot))
bot.run(TOKEN)