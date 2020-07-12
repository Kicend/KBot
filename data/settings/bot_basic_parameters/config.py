import time
from json import load
from os import environ

try:
    with open("data/settings/bot_basic_parameters/SECRET.json", "r") as f:
        secrets = load(f)
        TOKEN = secrets["DISCORD_TOKEN"]
        TOKEN_GENIUS = secrets["GENIUS_TOKEN"]
except FileNotFoundError:
    TOKEN = environ["DISCORD"]
    TOKEN_GENIUS = environ["GENIUS"]

# Podstawowe parametry bota
commands_prefix = "!"
version = "0.38"
boot_date = time.strftime("%H:%M %d.%m.%Y UTC")
__cogs__ = [
    "data.modules.cogs.Entertainment",
    "data.modules.cogs.Administration",
    "data.modules.cogs.Music",
    "data.modules.cogs.Utilities",
    "data.modules.cogs.Economy"
    ]
