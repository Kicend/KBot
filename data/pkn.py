# Zgodne z KBot 0.12-x
import discord
import random

async def rsp(self, ctx, hand):
    """Zagraj ze mną w papier, kamień i nożyce"""

    choices = ["papier", "kamień", "nożyce"]
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
        await ctx.send(komunikat.format(choice, p))
