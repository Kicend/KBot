# Zgodne z KBot 0.21-x

import asyncio
import discord
import json
import os
import youtube_dl
from data.lang.pl_PL import communicates_PL

server_players = {}
server_tools = {}
server_parameters = {}

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
    'source_address': '0.0.0.0'   # bind to ipv4 since ipv6 addresses cause issues sometimes
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
        self.voters_count = None
        self.voters = []
        self.vote_switch = 0
        self.is_paused = 0

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
            if self.vote_switch == 1:
                self.vote_switch = 0
                while self.voters != []:
                    del self.voters[0]
                await ctx.send("{}".format(communicates_PL.communicates.get(0)))
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

    async def pause(self, ctx):
        self.is_paused = 1
        self.save_time = self.now
        ctx.voice_client.pause()

    async def resume(self, ctx):
        self.is_paused = 0
        ctx.voice_client.resume()

    async def konwerter(self, czas):
        minuty = czas / 60
        sekundy = czas % 60
        if sekundy > 9:
            return "{}:{}".format(int(round(minuty - 0.5, 0)), sekundy)
        else:
            return "{}:0{}".format(int(round(minuty - 0.5, 0)), sekundy)

    async def current_time(self, czas: int):
        while self.now <= czas:
            self.now += 1
            await asyncio.sleep(1)
            if self.is_paused == 1:
                self.now = self.save_time

    async def vote_system(self, ctx):
        if self.vote_switch == 0:
            vc_members = discord.VoiceChannel = ctx.author.voice.channel
            self.voters_count = len(vc_members.members)
            self.voters.append(ctx.author)
            if self.voters_count - 1 == 1:
                await ctx.send("Pieśń została pominięta!")
                del self.gra[0]
                ctx.voice_client.stop()
                self.task.cancel()
                while self.voters != []:
                    del self.voters[0]
                asyncio.run(await Player.main(self, ctx))
            else:
                await ctx.send("Zagłosowało 1/{}".format(self.voters_count - 1))
                self.vote_switch = 1
        elif self.vote_switch == 1:
            if ctx.author in self.voters:
                await ctx.send("Już oddałeś głos!")
            elif ctx.author not in self.voters:
                self.voters.append(ctx.author)
                await ctx.send("Zagłosowało {}/{}".format(len(self.voters), self.voters_count - 1))
                if len(self.voters) >= round(self.voters_count/2 - 0.5, 0):
                    await ctx.send("Głosowanie za pominięciem przebiegło pomyślnie. Pieśń została pominięta!")
                    del self.gra[0]
                    ctx.voice_client.stop()
                    self.task.cancel()
                    while self.voters != []:
                        del self.voters[0]
                    self.vote_switch = 0
                    asyncio.run(await Player.main(self, ctx))

class Tools(object):
    def __init__(self, id):
        self.ban_users = []
        self.id = id

    async def banlist_display(self, ctx):
        banned_users = await ctx.guild.bans()

        for ban_entry in banned_users:
            user = ban_entry.user
            if user not in self.ban_users:
                self.ban_users.append(user)

        embed = discord.Embed(
            colour=discord.Colour.blue()
        )

        embed.set_author(name="Lista skazanych")

        if self.ban_users != []:
            for liczba, user in enumerate(self.ban_users):
                liczba = liczba + 1
                embed.add_field(name="Skazany nr {}".format(liczba), value=user, inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send("Lista skazanych jest pusta")

    async def banlist_refresh(self, ctx):
        banned_users = await ctx.guild.bans()

        for ban_entry in banned_users:
            user = ban_entry.user
            if user not in self.ban_users:
                self.ban_users.append(user)

    async def ban(self, ctx, member: discord.Member, reason):
        await member.ban(reason=reason)
        await ctx.send("Użyszkodnik został skazany na tułaczkę\nPowód: {}".format(reason))
        await Tools.banlist_refresh(self, ctx)

    async def unban(self, ctx, members):
        banned_users = await ctx.guild.bans()
        if members.count(","):
            await ctx.send("Nie używaj przecinków przy wymienianiu. Wystarczą spacje!")
            return

        members_list = members.split()

        for ban_entry in banned_users:
            user = ban_entry.user
            member = members_list.pop(0)
            if member.count("#"):
                member_name, member_discriminator = member.split("#")
                if (user.name, user.discriminator) == (member_name, member_discriminator):
                    await ctx.guild.unban(user)
                    await ctx.send("{} został odbanowany".format(user.mention))
            else:
                try:
                    member_number = int(member)
                    member = self.ban_users.pop(member_number - 1)
                    await ctx.guild.unban(member)
                    await ctx.send("{} został odbanowany".format(member.mention))
                except IndexError:
                    await ctx.send("Nie ma tylu skazańców!")

class GuildParameters(object):
    def __init__(self, id):
        self.id = id
        self.prefix = None
        self.filename = "data/settings/servers_settings/{}.json".format(self.id)
        self.filename_prefixes = "data/settings/servers_prefixes/prefixes.json"

    async def join_guild(self):
        guild_parameters = {"prefix": "!"}
        server_prefix = {str(self.id): "!"}
        if not os.path.isfile(self.filename):
            with open(self.filename, "a+") as f:
                json.dump(guild_parameters, f, indent=4)
                f.close()
        if not os.path.isfile(self.filename_prefixes):
            with open(self.filename_prefixes, "a+") as f:
                json.dump(server_prefix, f, indent=4)
                f.close()
        else:
            with open(self.filename_prefixes, "r+") as f:
                json.dump(server_prefix, f, indent=4)
                f.close()

    async def leave_guild(self):
        if os.path.isfile(self.filename):
            os.remove(self.filename)
        with open(self.filename_prefixes, "r+") as f:
            prefixes = json.load(f)
            del prefixes[str(self.id)]
            f.close()

    async def change_prefix(self, ctx, prefix: str):
        if os.path.isfile(self.filename_prefixes):
            with open(self.filename_prefixes, "r") as f:
                prefixes = json.load(f)
            with open(self.filename_prefixes, "w") as f:
                prefixes[str(self.id)] = prefix
                json.dump(prefixes, f, indent=4)
                f.close()
                await ctx.send("Prefix został pomyślnie zmieniony na '{}'".format(prefix))