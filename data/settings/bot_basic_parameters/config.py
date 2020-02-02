import time

# Podstawowe parametry bota
TOKEN = 'NTcwMjg4NTM0MDIwMTYxNTM4.XL9qbA.z2aE8-wAdad78ox3Dt-N8oswTVA'
TOKEN_GENIUS = "HS_xIb_SITDcN61C-qI-aVxNrpR0rhaKkp4aphnll-rPL11fZdqcmvoD-_MQf8gs"
commands_prefix = "!"
version = "0.34-1"
boot_date = time.strftime("%H:%M %d.%m.%Y UTC")
__cogs__ = [
    "data.modules.cogs.Entertainment",
    "data.modules.cogs.Administration",
    "data.modules.cogs.Music",
    "data.modules.cogs.Utilities",
    "data.modules.cogs.Economy"
    ]
