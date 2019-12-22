import os
import json
from data.modules.utils import constant as const

async def guild_check(bot):
    with open(const.SERVER_PREFIXES_FILE, "r") as f:
        servers_prefixes = json.load(f)
    for guild in bot.guilds:
        if not os.path.isfile("data/settings/servers_settings/{}.json".format(guild.id)):
            add_guild_config(guild.id, 0)
        if not str(guild.id) in servers_prefixes.keys():
            add_guild_config(guild.id, 1)

def add_guild_config(guild_id, mode: int):
    if mode == 0:
        guild_parameters = {"require_dj": "off", "QSP": "on", "autorole": None, "currency_symbol": "$"}
        with open("data/settings/servers_settings/{}.json".format(guild_id), "a+") as f:
            json.dump(guild_parameters, f, indent=4)

    elif mode == 1:
        with open(const.SERVER_PREFIXES_FILE, "r") as f:
            server_prefixes = json.load(f)
        with open(const.SERVER_PREFIXES_FILE, "w") as f:
            server_prefixes[str(guild_id)] = const.DEFAULT_SERVER_PREFIX
            json.dump(server_prefixes, f, indent=4)
