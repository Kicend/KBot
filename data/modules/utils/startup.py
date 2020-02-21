import os
import json
import discord
from data.settings.bot_basic_parameters import constant as const

guild_list = []
keys_to_delete = []

try:
    with open(const.SERVERS_PREFIXES_FILE, "r") as f:
        servers_prefixes = json.load(f)
except (FileNotFoundError, FileExistsError):
    os.makedirs("data/settings/servers_prefixes", exist_ok=True)
    with open(const.SERVERS_PREFIXES_FILE, "a") as f:
        servers_prefixes = {}
        json.dump(servers_prefixes, f, indent=4)

async def guild_check(bot):
    for guild in bot.guilds:
        exist = False
        guild_list.append(str(guild.id))
        if not os.path.isfile("data/settings/servers_settings/{}.json".format(guild.id)):
            add_guild_config(guild.id, 0)
        if not str(guild.id) in servers_prefixes.keys():
            add_guild_config(guild.id, 1)
        if not os.path.isfile(const.SERVERS_ECO_DB + "/{}.json".format(guild.id)):
            add_user_eco_info(guild.id, guild.members, 0)
            exist = True
        if not exist:
            with open(const.SERVERS_ECO_DB + "/{}.json".format(guild.id), "r") as db:
                guild_accounts = json.load(db)
            add_user_eco_info(guild.id, guild.members, 1, guild_accounts)
    remove_guild_config()
    remove_user_eco_info(bot)

def add_guild_config(guild_id, mode: int):
    if mode == 0:
        with open("data/settings/servers_settings/{}.json".format(guild_id), "a+") as s:
            json.dump(const.DEFAULT_GUILD_PARAMETERS, s, indent=4)

    elif mode == 1:
        with open(const.SERVERS_PREFIXES_FILE, "w") as p:
            servers_prefixes[str(guild_id)] = const.DEFAULT_SERVER_PREFIX
            json.dump(servers_prefixes, p, indent=4)

def remove_guild_config():
    for filename in os.listdir(const.SERVERS_SETTINGS_FILES):
        if filename[:-5] not in guild_list:
            os.remove(const.SERVERS_SETTINGS_FILES + "/" + filename)
    for guild_in_config in servers_prefixes.keys():
        if guild_in_config not in guild_list:
            keys_to_delete.append(guild_in_config)
    with open(const.SERVERS_PREFIXES_FILE, "w") as p:
        for element in keys_to_delete:
            del servers_prefixes[element]
        json.dump(servers_prefixes, p, indent=4)

def add_user_eco_info(guild_id, members_list, mode: int, guild_accounts=None):
    if mode == 0:
        with open(const.SERVERS_ECO_DB + "/{}.json".format(guild_id), "a") as db:
            members_accounts = {}
            for member in members_list:
                discord.User = member
                if member.bot is False:
                    members_accounts[str(member.id)] = 0
            json.dump(members_accounts, db, indent=4)

    elif mode == 1:
        for member in members_list:
            discord.User = member
            if member.bot is False and str(member.id) not in guild_accounts.keys():
                guild_accounts[str(member.id)] = 0
        with open(const.SERVERS_ECO_DB + "/{}.json".format(guild_id), "w") as db:
            json.dump(guild_accounts, db, indent=4)

def remove_user_eco_info(bot):
    for filename in os.listdir(const.SERVERS_ECO_DB):
        if filename[:-5] not in guild_list:
            os.remove(const.SERVERS_ECO_DB + "/" + filename)
    for guild in bot.guilds:
        with open(const.SERVERS_ECO_DB + "/{}.json".format(guild.id), "r") as db:
            guild_accounts = json.load(db)
        with open(const.SERVERS_ECO_DB + "/{}.json".format(guild.id), "w") as db:
            member_list = []
            account_to_delete = []
            for member in guild.members:
                discord.User = member
                if member.bot is False:
                    member_list.append(str(member.id))
            for account in guild_accounts.keys():
                if account not in member_list:
                    account_to_delete.append(account)
            for element in account_to_delete:
                del guild_accounts[element]
            json.dump(guild_accounts, db, indent=4)
