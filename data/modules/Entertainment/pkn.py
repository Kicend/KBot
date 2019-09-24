import random

async def rsp(self, ctx, hand: str):
    """Zagraj ze mną w papier, kamień i nożyce"""

    choices = ("papier", "kamień", "nożyce")
    choice = random.choice(choices)
    w = "Wygrałeś"
    p = "Przegrałeś"
    komunikat = "{} - {}"
    i = 0

    if hand == choice:
        await ctx.send("Remis")
        i += 1
    if hand == "papier" and choice == "kamień":
        await ctx.send(komunikat.format(choice, w))
        i += 1
    if hand == "kamień" and choice == "nożyce":
        await ctx.send(komunikat.format(choice, w))
        i += 1
    if hand == "nożyce" and choice == "papier":
        await ctx.send(komunikat.format(choice, w))
        i += 1
    if i == 0:
        if hand == "nożyce" or "papier" or "kamień":
            await ctx.send(komunikat.format(choice, p))
        else:
            await ctx.send("Ciekawe jak tak ułożyłeś rękę?")
