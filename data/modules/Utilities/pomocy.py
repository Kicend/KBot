import discord

async def pomocy(self, ctx, los, wersja):
    decyzja = int(los)
    if decyzja == 1:
        embed = discord.Embed(
            colour=discord.Colour.blue()
        )

        embed.set_author(name="Sekcja pomocy bota KBot wersja {} (strona 1/4)".format(wersja))
        embed.add_field(name="!wkrocz {nazwa kanału}", value="Wkracza z buta na czat głosowy", inline=False)
        embed.add_field(name="!strumykuj <url>", value="Strumykuj z interneta pieśni", inline=False)
        embed.add_field(name="!następna", value="Przewiń do kolejnej pieśni", inline=False)
        embed.add_field(name="!adminnext", value="Pomiń pieśń jak król", inline=False)
        embed.add_field(name="!pętla", value="Zapętlij pieśń", inline=False)
        embed.add_field(name="!info", value="Wyświetl informacje o aktualnie granej pieśni", inline=False)
        embed.add_field(name="!kolejka", value="Sprawdź zawartość kolejki", inline=False)
        embed.add_field(name="!czyść_kolejke", value="Wyczyść kolejkę z niepotrzebnych pieśni", inline=False)
        embed.add_field(name="!harmider <wartość (od 0 do 150)>", value="Zmienia głośnośc bota", inline=False)
        embed.add_field(name="!pauzuj", value="Pauzuje graną pieśń", inline=False)
        embed.add_field(name="!wznów", value="Wznawia wstrzymaną pieśń", inline=False)
        embed.add_field(name="!wypad", value="Zatrzymuje bota i rozłącza go z czatem głosowym", inline=False)

        await ctx.send(embed=embed)

    elif decyzja == 2:
        embed = discord.Embed(
            colour=discord.Colour.blue()
        )

        embed.set_author(name="Sekcja pomocy KBot wersja {} (strona 2/4)".format(wersja))
        embed.add_field(name="!ping", value="Dowiedz się jak słabego mam neta", inline=False)
        embed.add_field(name="!zaproszenie", value="We no zaproś na serwerek", inline=False)
        embed.add_field(name="!autor", value="Wpiszta by się dowiedzieć więcej o Stwórcy tego dzieła", inline=False)
        embed.add_field(name="!info_bot", value="Informacje o mnie", inline=False)
        embed.add_field(name="!serwer", value="Informacje o serwerze", inline=False)
        embed.add_field(name="!użytkownik <nick, @nick lub id>", value="Informacje o danym użytkowniku", inline=False)

        await ctx.send(embed=embed)

    elif decyzja == 3:
        embed = discord.Embed(
            colour=discord.Colour.blue()
        )

        embed.set_author(name="Sekcja pomocy KBot wersja {} (strona 3/4)".format(wersja))
        embed.add_field(name="!kopnij", value="Kopnij w tyłek", inline=False)
        embed.add_field(name="!ukarz", value="Ukarz delikwenta na tułaczkę", inline=False)
        embed.add_field(name="!wybacz", value="Wybacz mu", inline=False)
        embed.add_field(name="!skazańcy", value="Lista skazańców", inline=False)
        embed.add_field(name="!czyść <liczba> {użytkownik}", value="Służba sprzątania czatu", inline=False)
        embed.add_field(name="!dodaj_role <użytkownik> <rola>", value="Obdaruj użytkownika rolą", inline=False)
        embed.add_field(name="!usuń_role <użytkownik> <rola>", value="Zabierz nikczemnikowi rolę", inline=False)

        await ctx.send(embed=embed)

    elif decyzja == 4:
        embed = discord.Embed(
            colour=discord.Colour.blue()
        )

        embed.set_author(name="Sekcja pomocy KBot wersja {} (strona 4/4)".format(wersja))
        embed.add_field(name="!kostka <ile ścian (minimum 4)>", value="Weźse wylosuj jakąś liczbunie szefuńciu",
                        inline=False)
        embed.add_field(name="!zapytaj <pytanie>", value="Zapytaj mnie o cokolwiek", inline=False)
        embed.add_field(name="!pkn <papier, kamień lub nożyce>", value="Zagraj ze mną w papier, kamień i nożyce",
                        inline=False)
        embed.add_field(name="!zgadywanka", value="Odgadnij liczbę", inline=False)
        embed.add_field(name="!moneta", value="Rzuć monetą", inline=False)

        await ctx.send(embed=embed)


