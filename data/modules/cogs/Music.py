import asyncio
import lyricsgenius
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from youtube_search import YoutubeSearch
from data.modules.utils import core as cr
from data.settings.bot_basic_parameters import config

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["wkrocz"])
    async def join(self, ctx, *, channel: discord.VoiceChannel = None):
        """Wkracza z buta na czat głosowy"""
        server = self.bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in cr.server_parameters:
            cr.server_parameters[server_id] = cr.GuildParameters(server_id)
        has_permission = await cr.server_parameters[server_id].check_permissions(ctx, "DJ")
        if has_permission is True:
            if channel is None:
                channel = ctx.author.voice.channel
            if ctx.voice_client is not None:
                return await ctx.voice_client.move_to(channel)

            await channel.connect()
        else:
            await ctx.send("Nie posiadasz roli DJ!")

    @commands.command(aliases=["strumykuj"])
    async def play(self, ctx, *, url):
        """Strumykuj z interneta pieśni"""
        server = self.bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in cr.server_parameters:
            cr.server_parameters[server_id] = cr.GuildParameters(server_id)
        has_permission = await cr.server_parameters[server_id].check_permissions(ctx, "DJ")
        server_config = await cr.server_parameters[server_id].check_config()

        async def play_command_procedures(link):
            if server_id not in cr.server_players:
                cr.server_players[server_id] = cr.Player(server_id)
            if not cr.server_players[server_id].playing:
                await ctx.send("Rozpoczynam odtwarzanie")
                cr.server_players[server_id].queue.append(link)
                asyncio.run(await cr.server_players[server_id].main(ctx))
            else:
                if link in cr.server_players[server_id].queue:
                    url_in_queue = True
                else:
                    url_in_queue = False
                if server_config["QSP"] and url_in_queue is True:
                    await ctx.send("Nie możesz poczekać? Po co kolejna taka sama piosenka w kolejce?")
                elif server_config["QSP"] is False or url_in_queue is False:
                    cr.server_players[server_id].queue.append(link)
                    dictMeta = cr.ytdl.extract_info(link, download=False)
                    title = dictMeta['title']
                    cr.server_players[server_id].songs.append(title)
                    await ctx.send("Pieśń dodana do kolejki")

        if has_permission is True:
            if not url.count("https"):
                search_results = YoutubeSearch(url, max_results=10).to_dict()

                embed = discord.Embed(
                    colour=discord.Colour.blue()
                )

                embed.set_author(name="Wyniki wyszukiwania dla hasła {}".format(url))
                for number, result in enumerate(search_results):
                    embed.add_field(name="Propozycja nr {}".format(number+1),
                                    value="Tytuł: {}".format(result["title"]),
                                    inline=False)

                await ctx.send(embed=embed)
                await ctx.send("```Wybierz piosenkę wpisując odpowiednią cyfrę. Masz na to 10 sekund!```")
                try:
                    msg = await self.bot.wait_for("message", timeout=10)
                    if ctx.author.bot:
                        return None
                    else:
                        try:
                            cho = int(msg.content) - 1
                            url = "https://www.youtube.com" + search_results[cho]["link"]
                            await play_command_procedures(url)
                        except TypeError:
                            await ctx.send("Wiadomośc miała być liczbą!")
                except asyncio.TimeoutError:
                    await ctx.send("Czas minął")
            else:
                await play_command_procedures(url)
        else:
            await ctx.send("Nie posiadasz roli DJ!")

    @commands.command(aliases=["następna", "skip"])
    async def next(self, ctx):
        """Przewiń do kolejnej pieśni"""
        server = self.bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in cr.server_parameters:
            cr.server_parameters[server_id] = cr.GuildParameters(server_id)
        has_permission = await cr.server_parameters[server_id].check_permissions(ctx, "DJ")
        if has_permission is True:
            if server_id not in cr.server_players:
                cr.server_players[server_id] = cr.Player(server_id)
            if cr.server_players[server_id].queue:
                await ctx.send("Pieśń została pominięta przez DJ'a!")
                ctx.voice_client.stop()
                del cr.server_players[server_id].playing[0]
                cr.server_players[server_id].task.cancel()
                if cr.server_players[server_id].loop:
                    cr.server_players[server_id].loop = False
                if cr.server_players[server_id].vote_switch == 1:
                    cr.server_players[server_id].vote_switch = 0
                    await cr.server_players[server_id].vote_list_clear()
                asyncio.run(await cr.server_players[server_id].main(ctx))
        elif has_permission is False:
            if server_id not in cr.server_players:
                cr.server_players[server_id] = cr.Player(server_id)
            if cr.server_players[server_id].queue:
                await cr.server_players[server_id].vote_system(ctx)
        else:
            await ctx.send("Brak pieśni w kolejce")

    @commands.command(aliases=["adminskip"])
    @has_permissions(administrator=True)
    async def adminnext(self, ctx):
        """Pomiń pieśń jak król"""
        server = self.bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in cr.server_players:
            cr.server_players[server_id] = cr.Player(server_id)
        if cr.server_players[server_id].queue:
            await ctx.send("Pieśń została pominięta przez administratora!")
            ctx.voice_client.stop()
            del cr.server_players[server_id].playing[0]
            cr.server_players[server_id].task.cancel()
            if cr.server_players[server_id].vote_switch == 1:
                cr.server_players[server_id].vote_switch = 0
                await cr.server_players[server_id].vote_list_clear()
            asyncio.run(await cr.server_players[server_id].main(ctx))

    @commands.command(aliases=["cofnij_głos"])
    async def unvote(self, ctx):
        """Cofnij głos"""
        server = self.bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in cr.server_players:
            cr.server_players[server_id] = cr.Player(server_id)
        if cr.server_players[server_id].vote_switch == 1:
            if ctx.author in cr.server_players[server_id].voters:
                cr.server_players[server_id].voters.remove(ctx.author)
                await ctx.send("Pomyślnie wycofałeś swój głos!")
                if cr.server_players[server_id].voters:
                    await ctx.send("```Zagłosowało {}/{}```".format(len(cr.server_players[server_id].voters),
                                                                    cr.server_players[server_id].voters_count - 1))
                else:
                    cr.server_players[server_id].vote_switch = 0
                    await ctx.send("```Głosowanie za pominięciem zostało anulowane!```")
            else:
                await ctx.send("Nie zagłosowałeś wcześniej lub wycowałeś swój głos!")
        else:
            await ctx.send("Obecnie nie trwa żadne głosowanie!")

    @commands.command(aliases=["pętla"])
    async def loop(self, ctx):
        """Zapętlij pieśń"""
        server = self.bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in cr.server_parameters:
            cr.server_parameters[server_id] = cr.GuildParameters(server_id)
        has_permission = await cr.server_parameters[server_id].check_permissions(ctx, "DJ")
        if has_permission is True:
            if server_id not in cr.server_players:
                cr.server_players[server_id] = cr.Player(server_id)
            if cr.server_players[server_id].playing:
                if not cr.server_players[server_id].loop:
                    cr.server_players[server_id].loop = True
                    await ctx.send("Pieśń została zapętlona!")
                else:
                    cr.server_players[server_id].loop = False
                    await ctx.send("Pieśń została odpętlona!")
            else:
                await ctx.send("Żadna pieśń nie jest w tej chwili odtwarzana!")
        else:
            await ctx.send("Nie posiadasz roli DJ!")

    @commands.command(aliases=["teraz"])
    async def current(self, ctx):
        """Wyświetl informacje o aktualnie granej pieśni"""
        server = self.bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in cr.server_players:
            cr.server_players[server_id] = cr.Player(server_id)
        if cr.server_players[server_id].playing:
            dictMeta = cr.ytdl.extract_info(cr.server_players[server_id].playing[0], download=False)
            time = dictMeta['duration']

            embed = discord.Embed(
                colour=discord.Colour.blue()
            )

            embed.set_author(name="Aktualnie gra")
            embed.add_field(name="Tytuł:", value=dictMeta['title'], inline=False)
            embed.add_field(name="URL:", value=cr.server_players[server_id].playing[0], inline=False)
            embed.add_field(name="Czas:", value="{}/{}".format(
                            str(await cr.server_players[server_id].converter(cr.server_players[server_id].now)),
                            str(await cr.server_players[server_id].converter(time))), inline=False
                            )

            await ctx.send(embed=embed)
        else:
            await ctx.send("Nic nie gra, nie słychać?")

    @commands.command(aliases=["pauzuj"])
    async def pause(self, ctx):
        """Pauzuje graną pieśń"""
        server = self.bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in cr.server_parameters:
            cr.server_parameters[server_id] = cr.GuildParameters(server_id)
        has_permission = await cr.server_parameters[server_id].check_permissions(ctx, "DJ")
        if has_permission is True:
            if server_id not in cr.server_players:
                cr.server_players[server_id] = cr.Player(server_id)
            if cr.server_players[server_id].playing:
                await cr.server_players[server_id].pause(ctx)
                await ctx.send("Pieśń została zapauzowana")
            else:
                await ctx.send("Żadna pieśń nie jest w tej chwili odtwarzana!")
        else:
            await ctx.send("Nie posiadasz roli DJ!")

    @commands.command(aliases=["wznów"])
    async def resume(self, ctx):
        """Wznawia wstrzymaną pieśń"""
        server = self.bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in cr.server_parameters:
            cr.server_parameters[server_id] = cr.GuildParameters(server_id)
        has_permission = await cr.server_parameters[server_id].check_permissions(ctx, "DJ")
        if has_permission is True:
            if server_id not in cr.server_players:
                cr.server_players[server_id] = cr.Player(server_id)
            if cr.server_players[server_id].playing:
                await cr.server_players[server_id].resume(ctx)
                await ctx.send("Pieśń została wznowiona")
            else:
                await ctx.send("Żadna pieśń nie jest w tej chwili odtwarzana!")
        else:
            await ctx.send("Nie posiadasz roli DJ!")

    @commands.command(aliases=["harmider"])
    async def volume(self, ctx, volume: int):
        """Zmienia głośność bota"""
        server = self.bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in cr.server_parameters:
            cr.server_parameters[server_id] = cr.GuildParameters(server_id)
        has_permission = await cr.server_parameters[server_id].check_permissions(ctx, "DJ")
        if has_permission is True:
            if server_id not in cr.server_players:
                cr.server_players[server_id] = cr.Player(server_id)
            if volume > 150:
                await ctx.send("Zgłupiałeś, chcesz ogłuchnąć!?")
            elif volume < 0:
                await ctx.send("Co? Niby jak?")
            else:
                if ctx.voice_client is None:
                    return await ctx.send("Nie jest połączony z żadnym czatem głosowym")

                ctx.voice_client.source.volume = volume / 100
                await ctx.send("Głośność zmieniona na {}%".format(volume))
        else:
            await ctx.send("Nie posiadasz roli DJ!")

    @commands.command(aliases=["wypad"])
    async def leave(self, ctx):
        """Zatrzymuje bota i rozłącza go z czatem głosowym"""
        server = self.bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in cr.server_parameters:
            cr.server_parameters[server_id] = cr.GuildParameters(server_id)
        has_permission = await cr.server_parameters[server_id].check_permissions(ctx, "DJ")
        if has_permission is True:
            if server_id not in cr.server_players:
                cr.server_players[server_id] = cr.Player(server_id)
            await ctx.voice_client.disconnect()
            if cr.server_players[server_id].queue:
                cr.server_players[server_id].queue = []
                cr.server_players[server_id].songs = []
            if cr.server_players[server_id].playing:
                del cr.server_players[server_id].playing[0]
            del cr.server_players[server_id]
            await ctx.send("Pamięć podręczna została wyczyszczona")
        else:
            await ctx.send("Nie posiadasz roli DJ!")

    @commands.command(aliases=["czyść_kolejke"])
    async def clear_queue(self, ctx):
        """Wyczyść kolejkę z niepotrzebnych pieśni"""
        server = self.bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in cr.server_parameters:
            cr.server_parameters[server_id] = cr.GuildParameters(server_id)
        has_permission = await cr.server_parameters[server_id].check_permissions(ctx, "DJ")
        if has_permission is True:
            if server_id not in cr.server_players:
                cr.server_players[server_id] = cr.Player(server_id)
            if cr.server_players[server_id].queue:
                cr.server_players[server_id].queue = []
                cr.server_players[server_id].songs = []
            await ctx.send("Kolejka została wyczyszczona z pieśni")
        else:
            await ctx.send("Nie posiadasz roli DJ!")

    @commands.command(aliases=["kolejka"])
    async def queue(self, ctx, page: int = 1):
        """Sprawdź zawartość kolejki"""
        server = self.bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in cr.server_players:
            cr.server_players[server_id] = cr.Player(server_id)
        embed = discord.Embed(
            colour=discord.Colour.blue()
        )

        length = len(cr.server_players[server_id].songs)
        pages = round(length / 10 + 0.5, 0)
        if length % 10 == 0 and length/10 % 2 != 0:
            pages -= 1

        if page > pages:
            if not cr.server_players[server_id].songs:
                await ctx.send("Kolejka jest pusta")
            else:
                await ctx.send("Nie ma tylu stron! Aktualnie jest {}".format(int(pages)))
        else:
            if pages == 1:
                embed.set_author(name="Kolejka bota KBot")
            else:
                embed.set_author(name="Kolejka bota KBot {}/{}".format(page, int(pages)))

            for number, song in enumerate(cr.server_players[server_id].songs):
                if page * 10 - 10 <= number <= page * 10 - 1:
                    embed.add_field(name="Piosenka nr {}".format(number+1), value="{}".format(song),
                                    inline=False)

            await ctx.send(embed=embed)

    @commands.command(aliases=["tekst"])
    async def lyrics(self, ctx):
        """Wyświetlanie tekstu pieśni"""
        server = self.bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in cr.server_players:
            cr.server_players[server_id] = cr.Player(server_id)

        if cr.server_players[server_id].playing:
            genius = lyricsgenius.Genius(config.TOKEN_GENIUS)
            dictMeta = cr.ytdl.extract_info(cr.server_players[server_id].playing[0], download=False)
            song = genius.search_song(title=dictMeta["title"])
            await ctx.send(song.lyrics)
            await ctx.send("```"
                           "Tekst dostarczany przez Genius.com"
                           "```")
        else:
            await ctx.send("Nie gra żadna pieśń!")

    @play.before_invoke
    async def ensure_voice(self, ctx):
        server = self.bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in cr.server_parameters:
            cr.server_parameters[server_id] = cr.GuildParameters(server_id)
        has_permission = await cr.server_parameters[server_id].check_permissions(ctx, "DJ")
        if has_permission is True:
            if ctx.voice_client is None:
                if ctx.author.voice:
                    await ctx.author.voice.channel.connect()
                else:
                    raise commands.CommandError("Nie jesteś związany z żadnym czatem głosowym")

def setup(bot):
    bot.add_cog(Music(bot))
