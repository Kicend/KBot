import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
import asyncio
from data.modules import framework as fw

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["wkrocz"])
    async def join(self, ctx, *, channel: discord.VoiceChannel = None):
        """Wkracza z buta na czat głosowy"""
        if channel is None:
            channel = ctx.author.voice.channel
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command(aliases=["strumykuj"])
    async def play(self, ctx, *, url):
        """Strumykuj z interneta pieśni"""
        server = self.bot.get_guild(ctx.guild.id)
        server_id = server.id
        if not url.count("https"):
            await ctx.send("Wyszukiwanie muzyki zostało tymczasowo wyłączone. Przyjmowane są tylko adresy URL!")
        else:
            if server_id not in fw.server_players:
                fw.server_players[server_id] = fw.Player(server_id)
            if fw.server_players[server_id].gra == []:
                await ctx.send("Rozpoczynam odtwarzanie")
                fw.server_players[server_id].kolejka.append(url)
                asyncio.run(await fw.server_players[server_id].main(ctx))
            else:
                if url in fw.server_players[server_id].kolejka:
                    await ctx.send("Nie możesz poczekać? Po co druga taka sama piosenka w kolejce?")
                else:
                    fw.server_players[server_id].kolejka.append(url)
                    dictMeta = fw.ytdl.extract_info(url, download=False)
                    title = dictMeta['title']
                    fw.server_players[server_id].piosenki.append(title)
                    await ctx.send("Pieśń dodana do kolejki")

    @commands.command(aliases=["następna"])
    async def next(self, ctx):
        """Przewiń do kolejnej pieśni"""
        server = self.bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in fw.server_players:
            fw.server_players[server_id] = fw.Player(server_id)
        if fw.server_players[server_id].kolejka != []:
            await fw.server_players[server_id].vote_system(ctx)
        else:
            await ctx.send("Brak pieśni w kolejce")

    @commands.command()
    @has_permissions(administrator=True)
    async def adminnext(self, ctx):
        """Pomiń pieśń jak król"""
        server = self.bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in fw.server_players:
            fw.server_players[server_id] = fw.Player(server_id)
        if fw.server_players[server_id].kolejka != []:
            await ctx.send("Pieśń została pominięta przez administratora!")
            ctx.voice_client.stop()
            del fw.server_players[server_id].gra[0]
            fw.server_players[server_id].task.cancel()
            if fw.server_players[server_id].vote_switch == 1:
                fw.server_players[server_id].vote_switch = 0
                await fw.server_players[server_id].vote_list_clear()
            asyncio.run(await fw.server_players[server_id].main(ctx))

    @commands.command(aliases=["pętla"])
    async def loop(self, ctx):
        """Zapętlij pieśń"""
        server = self.bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in fw.server_players:
            fw.server_players[server_id] = fw.Player(server_id)
        if not fw.server_players[server_id].loop:
            fw.server_players[server_id].loop = True
            await ctx.send("Pieśń została zapętlona!")
        else:
            fw.server_players[server_id].loop = False
            await ctx.send("Pieśń została odpętlona!")

    @commands.command(aliases=["teraz"])
    async def current(self, ctx):
        """Wyświetl informacje o aktualnie granej pieśni"""
        server = self.bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in fw.server_players:
            fw.server_players[server_id] = fw.Player(server_id)
        if fw.server_players[server_id].gra != []:
            dictMeta = fw.ytdl.extract_info(fw.server_players[server_id].gra[0], download=False)
            czas = dictMeta['duration']

            embed = discord.Embed(
                colour=discord.Colour.blue()
            )

            embed.set_author(name="Aktualnie gra")
            embed.add_field(name="Tytuł:", value=dictMeta['title'], inline=False)
            embed.add_field(name="URL:", value=fw.server_players[server_id].gra[0], inline=False)
            embed.add_field(name="Czas:", value="{}/{}".format(str(await fw.server_players[server_id].konwerter(fw.server_players[server_id].now)), str(await fw.server_players[server_id].konwerter(czas))), inline=False)

            await ctx.send(embed=embed)
        else:
            await ctx.send("Nic nie gra, nie słychać?")

    @commands.command(aliases=["pauzuj"])
    async def pause(self, ctx):
        """Pauzuje graną pieśń"""
        server = self.bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in fw.server_players:
            fw.server_players[server_id] = fw.Player(server_id)
        await fw.server_players[server_id].pause(ctx)
        await ctx.send("Pieśń została zapauzowana")

    @commands.command(aliases=["wznów"])
    async def resume(self, ctx):
        """Wznawia wstrzymaną pieśń"""
        server = self.bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in fw.server_players:
            fw.server_players[server_id] = fw.Player(server_id)
        await fw.server_players[server_id].resume(ctx)
        await ctx.send("Pieśń została wznowiona")

    @commands.command(aliases=["harmider"])
    async def volume(self, ctx, volume: int):
        """Zmienia głośność bota"""
        if volume > 150:
            await ctx.send("Zgłupiałeś, chcesz ogłuchnąć!?")
        elif volume < 0:
            await ctx.send("Co? Niby jak?")
        else:
            if ctx.voice_client is None:
                return await ctx.send("Nie jest połączony z żadnym czatem głosowym")

            ctx.voice_client.source.volume = volume / 100
            await ctx.send("Głośność zmieniona na {}%".format(volume))

    @commands.command(aliases=["wypad"])
    @has_permissions(manage_channels=True)
    async def leave(self, ctx):
        """Zatrzymuje bota i rozłącza go z czatem głosowym"""
        server = self.bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in fw.server_players:
            fw.server_players[server_id] = fw.Player(server_id)
        await ctx.voice_client.disconnect()
        if fw.server_players[server_id].kolejka != []:
            while fw.server_players[server_id].kolejka != []:
                del fw.server_players[server_id].kolejka[0]
        if fw.server_players[server_id].piosenki != []:
            while fw.server_players[server_id].piosenki != []:
                del fw.server_players[server_id].piosenki[0]
        del fw.server_players[server_id].gra[0]
        del fw.server_players[server_id]
        await ctx.send("Pamięć podręczna została wyczyszczona")

    @commands.command(aliases=["czyść_kolejke"])
    async def delete_queue(self, ctx):
        """Wyczyść kolejkę z niepotrzebnych pieśni"""
        server = self.bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in fw.server_players:
            fw.server_players[server_id] = fw.Player(server_id)
        while fw.server_players[server_id].kolejka != []:
            del fw.server_players[server_id].kolejka[0]
        while fw.server_players[server_id].piosenki != []:
            del fw.server_players[server_id].piosenki[0]
        await ctx.send("Kolejka została wyczyszczona z pieśni")

    @commands.command(aliases=["kolejka"])
    async def queue(self, ctx):
        """Sprawdź zawartość kolejki"""
        server = self.bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in fw.server_players:
            fw.server_players[server_id] = fw.Player(server_id)
        embed = discord.Embed(
            colour=discord.Colour.blue()
        )

        embed.set_author(name="Kolejka bota KBot")

        for liczba, piosenka in enumerate(fw.server_players[server_id].piosenki):
            embed.add_field(name="{} - {}".format(liczba+1, piosenka), value="Piosenka nr {}".format(liczba+1), inline=False)
        if fw.server_players[server_id].piosenki == []:
            await ctx.send("Kolejka jest pusta")
        else:
            await ctx.send(embed=embed)

    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("Nie jesteś związany z żadnym czatem głosowym")
                raise commands.CommandError("Błąd, wleź na jakiś kanał głosowy")

def setup(bot):
    bot.add_cog(Music(bot))
