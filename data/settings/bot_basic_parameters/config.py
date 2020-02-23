import time
from data.settings.bot_basic_parameters import TOKENS

# Podstawowe parametry bota
TOKEN = TOKENS.DISCORD_BOT_TOKEN
TOKEN_GENIUS = TOKENS.GENIUS_TOKEN
commands_prefix = "!"
version = "0.34-3"
boot_date = time.strftime("%H:%M %d.%m.%Y UTC")
__cogs__ = [
    "data.modules.cogs.Entertainment",
    "data.modules.cogs.Administration",
    "data.modules.cogs.Music",
    "data.modules.cogs.Utilities",
    "data.modules.cogs.Economy"
    ]
