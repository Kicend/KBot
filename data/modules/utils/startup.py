import os
import json
from data.settings.bot_basic_parameters import constant as const

guild_list = []
keys_to_delete = []

with open(const.SERVERS_PREFIXES_FILE, "r") as f:
    servers_prefixes = json.load(f)

async def guild_check(bot):
    for guild in bot.guilds:
        guild_list.append(str(guild.id))
        if not os.path.isfile("data/settings/servers_settings/{}.json".format(guild.id)):
            add_guild_config(guild.id, 0)
        if not str(guild.id) in servers_prefixes.keys():
            add_guild_config(guild.id, 1)
    remove_guild_config()

def add_guild_config(guild_id, mode: int):
    if mode == 0:
        with open("data/settings/servers_settings/{}.json".format(guild_id), "a+") as s:
            json.dump(const.DEFAULT_GUILD_PARAMETERS, s, indent=4)

    elif mode == 1:
        with open(const.SERVERS_PREFIXES_FILE, "r") as p:
            server_prefixes = json.load(p)
        with open(const.SERVERS_PREFIXES_FILE, "w") as p:
            server_prefixes[str(guild_id)] = const.DEFAULT_SERVER_PREFIX
            json.dump(server_prefixes, p, indent=4)

def remove_guild_config():
    for filename in os.listdir(const.SERVERS_SETTINGS_FILES):
        if int(filename[:-5]) not in guild_list:
            os.remove(const.SERVERS_SETTINGS_FILES + "/" + filename)
    for guild_in_config in servers_prefixes.keys():
        if guild_in_config not in guild_list:
            keys_to_delete.append(guild_in_config)
    with open(const.SERVERS_PREFIXES_FILE, "w") as p:
        for element in keys_to_delete:
            del servers_prefixes[element]
        json.dump(servers_prefixes, p, indent=4)
