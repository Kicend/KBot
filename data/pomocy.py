# Zgodne z KBot 0.10-x
import discord

async def pomocy(self, ctx, los, wersja):
    decyzja = int(los)
    if decyzja == 1:
        author = "Kicend#2690"  # Nick autora (może kiedyś)

        embed = discord.Embed(
            colour=discord.Colour.blue()
        )

        embed.set_author(name="Sekcja pomocy bota KBot wersja {} (strona 1/3)".format(wersja))
        embed.add_field(name="!wkrocz <nazwa kanału>", value="Wkracza z buta na czat głosowy", inline=False)
        embed.add_field(name="!strumykuj <url>", value="Strumykuj z interneta pieśni", inline=False)
        embed.add_field(name="!zagraj <lokalizacja pliku (ścieżka bezwzlędna)>", value="Zagrywa pieśń z lokalnego komputera", inline=False)
        embed.add_field(name="!następna", value="Przewiń do kolejnej pieśni", inline=False)
        embed.add_field(name="!pętla <0 lub 1>", value="Zapętlij pieśń", inline=False)
        embed.add_field(name="!info", value="Wyświetl informacje o aktualnie granej pieśni", inline=False)
        embed.add_field(name="!kolejka", value="Sprawdź zawartość kolejki", inline=False)
        embed.add_field(name="!czyść", value="Wyczyśc kolejkę z niepotrzebnych pieśni", inline=False)
        embed.add_field(name="!harmider <wartość (od 0 do 150)>", value="Zmienia głośnośc bota", inline=False)
        embed.add_field(name="!stopuj", value="Stopuje aktualnie graną pieśń", inline=False)
        embed.add_field(name="!wypad", value="Zatrzymuje bota i rozłącza go z czatem głosowym", inline=False)

        await ctx.send(author, embed=embed)  # Jeżeli wstawiony author to await ctx.send(author, embed=embed)

    if decyzja == 2:
        author = ctx.message.author

        embed = discord.Embed(
            colour=discord.Colour.blue()
        )

        embed.set_author(name="Sekcja pomocy KBot wersja {} (strona 2/3)".format(wersja))
        embed.add_field(name="!kostka <ile ścian (minimum 4)>", value="Weźse wylosuj jakąś liczbunie szefuńciu",
                        inline=False)
        embed.add_field(name="!zapytaj <pytanie>", value="Zapytaj mnie o cokolwiek", inline=False)
        embed.add_field(name="!pkn <papier, kamień lub nożyce>", value="Zagraj ze mną w papier, kamień i nożyce",
                        inline=False)
        embed.add_field(name="!ping", value="Dowiedz się jak słabego mam neta", inline=False)
        embed.add_field(name="!zaproszenie", value="We no zaproś na serwerek", inline=False)
        embed.add_field(name="!autor", value="Wpiszta by się dowiedzieć więcej o Stwórcy tego dzieła", inline=False)

        await ctx.send(author, embed=embed)

    if decyzja == 3:
        author = ctx.message.author

        embed = discord.Embed(
            colour=discord.Colour.blue()
        )

        embed.set_author(name="Sekcja pomocy KBot wersja {} (strona 3/3)".format(wersja))
        embed.add_field(name="!kopnij", value="Kopnij w tyłek", inline=False)
        embed.add_field(name="!ukarz", value="Ukarz delikwenta na tułaczkę", inline=False)
        embed.add_field(name="!wybacz", value="Wybacz mu", inline=False)
        embed.add_field(name="!skazańcy", value="Lista skazańców", inline=False)

        await ctx.send(author, embed=embed)
