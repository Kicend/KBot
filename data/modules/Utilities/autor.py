import discord

async def autor(ctx):
    """Wpiszta by się dowiedzieć więcej o Stwórcy tego dzieła"""
    embed = discord.Embed(
        colour=discord.Colour.blue()
    )

    embed.set_author(name="Sekcja poświęcona Stwórcy tego wspaniałego dzieła KBot")
    embed.add_field(name="O mnie",
                    value="Jestem zwykłym chłopakiem siedzącym przed kompem i se postanowiłem napisać to, to tyle",
                    inline=False)
    embed.add_field(name="Technologia",
                    value="Dziękuję za stworzenie Discord.py wersja 1.2.3 \n""https://github.com/Rapptz/discord.py",
                    inline=False)
    embed.add_field(name="Technologia cd.",
                    value="Dziękuję również za stworzenie youtube_dl \n""https://github.com/ytdl-org/youtube-dl",
                    inline=False)
    embed.add_field(name="Podziękowania", value="Dzięki też, że w ogóle chciało Ci się to dodawać na serwa",
                    inline=False)

    await ctx.send(embed=embed)
