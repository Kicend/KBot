import asyncio
import discord
import json
import os
import youtube_dl
from data.lang.pl_PL import communicates_PL
from data.settings.bot_basic_parameters import constant as const
from warnings import filterwarnings

server_players = {}
server_tools = {}
server_parameters = {}
server_economy = {}

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
        return cls(discord.FFmpegPCMAudio(
            filename, **ffmpeg_options,
            before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -loglevel 'quiet'"),
            data=data
        )

class Player(object):
    def __init__(self, id):
        self.now = 0
        self.save_time = 0
        self.id = id
        self.queue = []
        self.songs = []
        self.playing = []
        self.voters_count = None
        self.voters = []
        self.vote_switch = 0
        self.is_paused = 0
        self.loop = False
        self.task = None

    async def main(self, ctx):
        self.task = asyncio.create_task(Player.player(self, ctx))
        await self.task

    async def player(self, ctx):
        while True:
            self.now = 0
            self.playing.append(self.queue[0])
            url = self.queue.pop(0)
            player = await YTDLSource.from_url(url, loop=False, stream=True)
            ctx.voice_client.play(player, after=lambda e: print('Błąd bota: %s' % e) if e else None)

            await ctx.send('Teraz muzykuję: {}'.format(player.title))
            dictMeta = ytdl.extract_info(url, download=False)
            duration = dictMeta['duration']
            if self.songs:
                del self.songs[0]
            await Player.current_time(self, duration)
            if self.loop:
                await Player.loop_player(self, ctx)
            del self.playing[0]
            if self.vote_switch == 1:
                self.vote_switch = 0
                while self.voters:
                    del self.voters[0]
                await ctx.send("{}".format(communicates_PL.communicates.get(0)))
            if self.playing == [] and self.queue == []:
                await ctx.send("Odtwarzacz kończy pracę")
                break
        await asyncio.sleep(30)
        if self.playing != [] or self.queue != []:
            return None
        else:
            await ctx.voice_client.disconnect()
            await asyncio.sleep(30)
            if self.playing != [] or self.queue != []:
                return None
            else:
                del server_players[self.id]

    async def loop_player(self, ctx):
        url = self.playing[0]
        dictMeta = ytdl.extract_info(url, download=False)
        duration = dictMeta['duration']
        while self.loop:
            self.now = 0
            player = await YTDLSource.from_url(url, loop=False, stream=True)
            ctx.voice_client.play(player, after=lambda e: print('Błąd bota: %s' % e) if e else None)

            await Player.current_time(self, duration)

    async def pause(self, ctx):
        self.is_paused = 1
        self.save_time = self.now
        ctx.voice_client.pause()

    async def resume(self, ctx):
        self.is_paused = 0
        ctx.voice_client.resume()

    @staticmethod
    async def converter(time):
        hours = 0
        minutes = time / 60
        if minutes >= 60:
            hours = minutes / 60
            minutes = round(minutes - 0.5, 0) - 60
            if minutes == 60:
                minutes = 0
            if hours < 1:
                hours = 0
        seconds = time % 60
        if minutes == 1:
            minutes += 0.1
        if hours == 1:
            hours += 0.1
        if seconds > 9 and hours == 0:
            return "{}:{}".format(int(round(minutes - 0.5, 0)), seconds)
        elif seconds <= 9 and minutes <= 59 and hours < 1:
            return "{}:0{}".format(int(round(minutes - 0.5, 0)), seconds)
        elif seconds > 9 and minutes > 9 and hours != 0:
            return "{}:{}:{}".format(int(round(hours - 0.5, 0)), int(round(minutes - 0.5, 0)), seconds)
        elif seconds <= 9 and minutes > 9 and hours != 0:
            return "{}:{}:0{}".format(int(round(hours - 0.5, 0)), int(round(minutes - 0.5, 0)), seconds)
        elif seconds > 9 and minutes < 9 and hours != 0:
            return "{}:0{}:{}".format(int(round(hours - 0.5, 0)), int(round(minutes - 0.5, 0)), seconds)
        elif seconds < 9 and minutes < 9 and hours != 0:
            return "{}:0{}:0{}".format(int(round(hours - 0.5, 0)), int(round(minutes - 0.5, 0)), seconds)
        else:
            return "**BŁĄD**: Konwerter nie mógł przeliczyć podanego czasu"

    async def current_time(self, time: int):
        while self.now <= time:
            self.now += 1
            await asyncio.sleep(1)
            if self.is_paused == 1:
                self.now = self.save_time

    async def vote_list_clear(self):
        while self.voters:
            del self.voters[0]

    async def vote_system(self, ctx):
        filterwarnings("ignore", category=RuntimeWarning)
        if self.vote_switch == 0:
            vc_members = discord.VoiceChannel = ctx.author.voice.channel
            self.voters_count = len(vc_members.members)
            self.voters.append(ctx.author)
            if self.voters_count - 1 == 1:
                await ctx.send("Pieśń została pominięta!")
                del self.playing[0]
                ctx.voice_client.stop()
                self.task.cancel()
                self.loop = False
                await Player.vote_list_clear(self)
                asyncio.run(Player.main(self, ctx))
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
                    del self.playing[0]
                    ctx.voice_client.stop()
                    self.task.cancel()
                    self.loop = False
                    await Player.vote_list_clear(self)
                    self.vote_switch = 0
                    asyncio.run(Player.main(self, ctx))

class Tools(object):
    def __init__(self, id):
        self.ban_users = []
        self.id = id

    async def banlist_display(self, ctx, page: int = 1):
        banned_users = await ctx.guild.bans()

        for ban_entry in banned_users:
            user = ban_entry.user
            if user not in self.ban_users:
                self.ban_users.append(user)

        embed = discord.Embed(
            colour=discord.Colour.blue()
        )

        length = len(banned_users)
        pages = round(length / 10 + 0.5, 0)
        if length % 10 == 0 and length/10 % 2 != 0:
            pages -= 1

        if page > pages:
            if not self.ban_users:
                await ctx.send("Lista skazanych jest pusta")
            else:
                await ctx.send("Nie ma tylu stron! Aktualnie jest {}".format(int(pages)))
        else:
            if pages == 1:
                embed.set_author(name="Lista skazanych")
            else:
                embed.set_author(name="Lista skazanych {}/{}".format(page, int(pages)))

            for number, user in enumerate(self.ban_users):
                if page * 10 - 10 <= number <= page * 10 - 1:
                    embed.add_field(name="Skazany nr {}".format(number+1), value=user, inline=False)

            await ctx.send(embed=embed)

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
        self.require_dj = None
        self.filename = const.SERVERS_SETTINGS_FILES + "/{}.json".format(self.id)
        self.filename_prefixes = const.SERVERS_PREFIXES_FILE
        self.eco_filename = const.SERVERS_ECO_DB + "/{}.json".format(self.id)

    async def join_guild(self):
        guild_parameters = {"require_dj": "off", "QSP": "on", "autorole": None, "currency_symbol": "$"}
        server_prefix = "!"
        if not os.path.isfile(self.filename):
            with open(self.filename, "a+") as f:
                json.dump(guild_parameters, f, indent=4)
        with open(self.filename_prefixes, "r") as f:
            server_prefixes = json.load(f)
        if not str(self.id) in server_prefixes.keys():
            with open(self.filename_prefixes, "w") as f:
                server_prefixes[str(self.id)] = server_prefix
                json.dump(server_prefixes, f, indent=4)

    async def leave_guild(self):
        if os.path.isfile(self.filename):
            os.remove(self.filename)
        if os.path.isfile(self.eco_filename):
            os.remove(self.eco_filename)
        with open(self.filename_prefixes, "r") as f:
            prefixes = json.load(f)
        with open(self.filename_prefixes, "w") as f:
            del prefixes[str(self.id)]
            if prefixes:
                json.dump(prefixes, f, indent=4)

    async def get_prefix(self):
        with open(self.filename_prefixes, "r") as f:
            prefixes = json.load(f)
            server_prefix = prefixes[str(self.id)]
        return server_prefix

    async def change_prefix(self, ctx, prefix: str):
        if os.path.isfile(self.filename_prefixes):
            with open(self.filename_prefixes, "r") as f:
                prefixes = json.load(f)
            with open(self.filename_prefixes, "w") as f:
                prefixes[str(self.id)] = prefix
                json.dump(prefixes, f, indent=4)
                await ctx.send("Prefix został pomyślnie zmieniony na '{}'".format(prefix))

    async def check_permissions(self, ctx, role: str):
        if self.require_dj is None:
            with open(self.filename, "r") as f:
                guild_parameters = json.load(f)
                self.require_dj = guild_parameters["require_dj"]
        if self.require_dj == "on":
            user_ext_info: discord.Member = ctx.author
            role = discord.utils.get(ctx.guild.roles, name=role)
            if role is None:
                await ctx.send("Serwer nie posiada roli DJ!")
            else:
                if role in user_ext_info.roles:
                    return True
                else:
                    return False
        elif self.require_dj == "off":
            return True

    async def check_config(self):
        with open(self.filename, "r") as f:
            config = json.load(f)
        return config

    async def change_config(self, setting: tuple):
        config = await GuildParameters.check_config(self)
        with open(self.filename, "w") as f:
            config[setting[0]] = setting[1]
            json.dump(config, f, indent=4)

class EcoMethods(object):
    def __init__(self, id):
        self.id = id
        self.members_accounts = EcoMethods.check_accounts(self)
        self.eco_filename = const.SERVERS_ECO_DB + "/{}.json".format(self.id)

    async def join_guild(self, guild: discord.Guild, i: int):
        members_list = guild.members
        members_accounts = {}
        for member in members_list:
            discord.User = member
            if member.bot is False:
                members_accounts[str(member.id)] = 0
        if i == 0:
            with open(self.eco_filename, "a") as f:
                json.dump(members_accounts, f, indent=4)
        else:
            with open(self.eco_filename, "w") as f:
                json.dump(members_accounts, f, indent=4)

    async def modify_eco_filename(self, member: discord.User, i: int):
        with open(self.eco_filename, "r") as f:
            members_accounts = json.load(f)
        if member.bot is False:
            if i == 0:
                with open(self.eco_filename, "w") as f:
                    members_accounts[str(member.id)] = 0
                    json.dump(members_accounts, f, indent=4)
            else:
                with open(self.eco_filename, "w") as f:
                    del members_accounts[str(member.id)]
                    if members_accounts:
                        json.dump(members_accounts, f, indent=4)

    async def check_accounts(self):
        with open(self.eco_filename, "r") as f:
            accounts = json.load(f)
        return accounts

    async def check_account(self, user_account: str):
        with open(self.eco_filename, "r") as f:
            accounts = json.load(f)
        money = accounts[user_account]
        return money

    async def money_transfer(self, sender_id: str, receiver_id: str, account_sender: int, account_receiver: int):
        with open(self.eco_filename, "r") as f:
            accounts = json.load(f)
        with open(self.eco_filename, "w") as f:
            accounts[sender_id] = account_sender
            accounts[receiver_id] = account_receiver
            json.dump(accounts, f, indent=4)

    async def change_money(self, receiver_id: str, account_receiver: int):
        with open(self.eco_filename, "r") as f:
            accounts = json.load(f)
        with open(self.eco_filename, "w") as f:
            accounts[receiver_id] = account_receiver
            json.dump(accounts, f, indent=4)

# Zbiór małych funkcji
def sortSecond(value):
    return value[1]
