import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from data.modules.utils import core as cr

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["przelej"])
    async def pay(self, ctx, user: discord.User, amount: int):
        server = self.bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in cr.server_economy:
            cr.server_economy[server_id] = cr.EcoMethods(server_id)
        if ctx.author.id == user.id:
            await ctx.send("Nie ma sensu dawać sobie pieniądze, przecież już je masz!")
        elif user.bot is True:
            await ctx.send("Boty nie posiadają konta bankowego!")
        else:
            if amount < 0:
                await ctx.send("Nie możesz płacić ujemną kwotą!")
            elif amount == 0:
                await ctx.send("Po co zawracasz głowę, skoro nie chcesz płacić!?")
            else:
                accounts = await cr.server_economy[server_id].check_accounts()
                sender = str(ctx.author.id)
                receiver = str(user.id)
                if accounts[receiver] + amount > 1000000000:
                    await ctx.send("Nie możesz przelać pieniędzy, ponieważ limit wynosi 1 000 000 000!")
                else:
                    account_sender = accounts[sender]
                    account_receiver = accounts[receiver]
                    if account_sender < amount:
                        await ctx.send("Nie masz wystarczających środków na koncie!")
                    else:
                        account_sender -= amount
                        account_receiver += amount
                        await cr.server_economy[server_id].money_transfer(
                            sender, receiver, account_sender, account_receiver
                        )
                        await ctx.send("Transakcja wykonana pomyślnie!\n"
                                       "Twój stan konta wynosi teraz {} $!".format(account_sender))

    @commands.command(aliases=["stan_konta"])
    async def money(self, ctx, user: discord.User = None):
        server = self.bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in cr.server_economy:
            cr.server_economy[server_id] = cr.EcoMethods(server_id)
        if user is None or user.id == ctx.author.id:
            money = await cr.server_economy[server_id].check_account(str(ctx.author.id))
            await ctx.send("Posiadasz {} $ na koncie".format(money))
        else:
            money = await cr.server_economy[server_id].check_account(str(user.id))
            await ctx.send("{} posiada {} $ na koncie".format(user.name, money))

    @commands.command(aliases=["dodaj_pieniądze"])
    @has_permissions(administrator=True)
    async def add_money(self, ctx, user: discord.User, amount: int):
        server = self.bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in cr.server_economy:
            cr.server_economy[server_id] = cr.EcoMethods(server_id)
        if user.bot is True:
            await ctx.send("Nie możesz dodać pieniędzy botu. Nie posiada konta bankowego!")
        elif amount <= 0:
            await ctx.send("Nieprawidłowa kwota do dodania!")
        else:
            accounts = await cr.server_economy[server_id].check_accounts()
            receiver = str(user.id)
            if accounts[receiver] + amount > 1000000000:
                await ctx.send("Nie możesz dodać pieniędzy, ponieważ limit wynosi 1 000 000 000!")
            else:
                account_receiver = accounts[receiver] + amount
                await cr.server_economy[server_id].add_money(receiver, account_receiver)
                if user.id == ctx.author.id:
                    await ctx.send("Dodałeś sobie {} $ na konto!\n"
                                   "Twój stan konta wynosi teraz {} $!".format(amount, account_receiver))
                else:
                    await ctx.send("Dodałeś {} $ na konto użytkownika {}\n"
                                   "Jego stan konta wynosi teraz {} $".format(amount, user.name, account_receiver))

    @commands.command(aliases=["reset_ekonomii"])
    @has_permissions(administrator=True)
    async def reset_eco(self, ctx):
        server = self.bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in cr.server_economy:
            cr.server_economy[server_id] = cr.EcoMethods(server_id)
        await cr.server_economy[server_id].join_guild(ctx.guild, 1)
        await ctx.send("Ekonomia została zresetowana!")

    @commands.command(aliases=["lista_kont"])
    async def leaderboard(self, ctx):
        server = self.bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in cr.server_economy:
            cr.server_economy[server_id] = cr.EcoMethods(server_id)
        accounts = await cr.server_economy[server_id].check_accounts()
        a = []
        for account in accounts:
            a.append((account, accounts[account]))
        accounts_sorted = sorted(a, key=cr.sortSecond, reverse=True)
        embed = discord.Embed(
            colour=discord.Colour.blue()
        )

        embed.set_author(name="Lista wszystkich kont na serwerze {}".format(ctx.guild.name))

        for liczba, account in enumerate(accounts_sorted):
            user = ctx.guild.get_member(int(account[0]))
            embed.add_field(name="Pozycja nr {}".format(liczba+1),
                            value="{} - {} $".format(user, account[1]), inline=False)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Economy(bot))
