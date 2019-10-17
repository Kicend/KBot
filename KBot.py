import asyncio
import discord
from discord.ext import commands
from itertools import cycle
import json

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

bot = commands.Bot(command_prefix=get_prefix, description='KBot wersja {}'.format(config.wersja))

bot.remove_command("help")

status = ["KBot {}".format(config.wersja), "!pomocy <1-4>"]

@bot.event
async def on_connect():
    print("Bot pomyślnie połączył się z Discordem\nTrwa wczytywanie danych...")
    for cog in config.__cogs__:
        try:
            bot.load_extension(cog)
        except:
            print("Nie udało się załadować rozszerzenia {}".format(cog))

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
async def on_guild_join(guild):
    server_id = guild.id
    if server_id not in cr.server_parameters:
        cr.server_parameters[server_id] = cr.GuildParameters(server_id)
    if server_id not in cr.server_economy:
        cr.server_economy[server_id] = cr.EcoMethods(server_id)

    await cr.server_parameters[server_id].join_guild()
    await cr.server_economy[server_id].join_guild(guild, 0)

@bot.event
async def on_guild_leave(guild):
    server_id = guild.id
    if server_id not in cr.server_parameters:
        cr.server_parameters[server_id] = cr.GuildParameters(server_id)

    await cr.server_parameters[server_id].leave_guild()

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
