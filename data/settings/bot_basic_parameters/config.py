import time

# Podstawowe parametry bota
TOKEN = 'NTcwMjg4NTM0MDIwMTYxNTM4.XL9qbA.z2aE8-wAdad78ox3Dt-N8oswTVA'
commands_prefix = "!"
wersja = "0.29"
boot_date = time.strftime("%H:%M %d.%m.%Y UTC")
__cogs__ = [
    "data.modules.cogs.Entertainment",
    "data.modules.cogs.Administration",
    "data.modules.cogs.Music",
    "data.modules.cogs.Utilities",
    "data.modules.cogs.Economy"
    ]
