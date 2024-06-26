#! /usr/bin/python3
import asyncio
import json
import discord
from discord.ext import commands
from itertools import cycle
from data.modules.utils import startup

# Importowanie rdzenia
from data.modules.utils import core as cr

# Importowanie konfiguracji bota
from data.settings.bot_basic_parameters import config

# Importowanie polskich komunikatów błędów
from data.lang.pl_PL import communicates_PL

# Importowanie listy emoji
# from data.reactions import reactions_db

def get_prefix(bot, message):
    with open("data/settings/servers_prefixes/prefixes.json", "r") as f:
        prefixes = json.load(f)

    return prefixes[str(message.guild.id)]

bot = commands.Bot(command_prefix=get_prefix, description='KBot wersja {}'.format(config.version))
cr.share.append(bot)
bot.remove_command("help")
status = ["KBot {}".format(config.version), "!pomocy <1-5>"]

@bot.event
async def on_connect():
    print("Bot pomyślnie połączył się z Discordem\nTrwa wczytywanie danych...")
    for cog in config.__cogs__:
        try:
            bot.load_extension(cog)
        except discord.ext.commands.errors.NoEntryPointError:
            print("Nie udało się załadować rozszerzenia {}".format(cog))

@bot.event
async def on_ready():
    print('Zalogowany jako {0} ({0.id})'.format(bot.user))
    print('----------------------------------------------')
    await startup.guild_check(bot)
    for guild in bot.guilds:
        print("{} ID: {}".format(guild.name, guild.id))
    msgs = cycle(status)
    while not bot.is_closed():
        current_status = next(msgs)
        game = discord.Game(current_status)
        await bot.change_presence(status=discord.Status.online, activity=game)
        await asyncio.sleep(5)

@bot.event
async def on_guild_join(guild):
    server_id = guild.id
    if server_id not in cr.server_parameters:
        cr.server_parameters[server_id] = cr.GuildParameters(server_id)
    if server_id not in cr.server_economy:
        cr.server_economy[server_id] = cr.EcoMethods(server_id)

    await cr.server_parameters[server_id].join_guild()
    await cr.server_economy[server_id].join_guild(guild, 0)

@bot.event
async def on_guild_remove(guild):
    server_id = guild.id
    if server_id not in cr.server_parameters:
        cr.server_parameters[server_id] = cr.GuildParameters(server_id)

    await cr.server_parameters[server_id].leave_guild()

@bot.event
async def on_member_join(member):
    server_id = member.guild.id
    if server_id not in cr.server_economy:
        cr.server_economy[server_id] = cr.EcoMethods(server_id)
    if server_id not in cr.server_parameters:
        cr.server_parameters[server_id] = cr.GuildParameters(server_id)

    await cr.server_economy[server_id].modify_eco_filename(member, 0)
    server_config = await cr.server_parameters[server_id].check_config()
    autorole = server_config["autorole"]
    if autorole is not None:
        autorole_id = autorole[-18:]
        role = discord.utils.get(member.guild.roles, id=int(autorole_id))
        await member.add_roles(role)

@bot.event
async def on_member_remove(member):
    server_id = member.guild.id
    if server_id not in cr.server_economy:
        cr.server_economy[server_id] = cr.EcoMethods(server_id)

    await cr.server_economy[server_id].modify_eco_filename(member, 1)

@bot.event
async def on_voice_state_update(member, before, after):
    event_vc = None
    server_id = member.guild.id
    for voice_client in bot.voice_clients:
        if voice_client.guild.id == member.guild.id:
            event_vc = voice_client
    if event_vc in bot.voice_clients:
        if server_id not in cr.server_players:
            cr.server_players[server_id] = cr.Player(server_id)
        if before.channel is None and cr.server_players[server_id].vote_switch == 1 and member.bot is False:
            cr.server_players[server_id].voters_count += 1
        elif after.channel is None and cr.server_players[server_id].vote_switch == 1 and member.bot is False:
            if member in cr.server_players[server_id].voters:
                del cr.server_players[server_id].voters[member]
        if cr.server_players[server_id].vote_switch == 1:
            await cr.server_players[server_id].vote_system(cr.server_players[server_id].vote_context, True)

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
            error = communicates_PL.errors_PL.get(0)
        await ctx.send(error)

bot.run(config.TOKEN)
