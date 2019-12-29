import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from data.modules.utils import core as cr
from data.settings.bot_basic_parameters import config

class Administration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["kopnij"])
    @has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="Brak"):
        """Kopnij w tyłek"""
        await member.kick(reason=reason)
        await ctx.send("Użyszkodnik został kopnięty\nPowód: {}".format(reason))

    @commands.command(aliases=["ukarz"])
    @has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="Brak"):
        """Ukarz delikwenta na tułaczkę"""
        server = self.bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in cr.server_tools:
            cr.server_tools[server_id] = cr.Tools(server_id)

        await cr.server_tools[server_id].ban(ctx, member, reason)

    @commands.command(aliases=["wybacz"])
    @has_permissions(ban_members=True)
    async def unban(self, ctx, *, members):
        """Wybacz mu"""
        server = self.bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in cr.server_tools:
            cr.server_tools[server_id] = cr.Tools(server_id)

        await cr.server_tools[server_id].unban(ctx, members)

    @commands.command(aliases=["skazańcy"])
    @has_permissions(manage_guild=True)
    async def banlist(self, ctx, page: int = 1):
        """Lista skazańców"""
        server = self.bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in cr.server_tools:
            cr.server_tools[server_id] = cr.Tools(server_id)

        await cr.server_tools[server_id].banlist_display(ctx, page)

    @commands.command(aliases=["ustawienia"])
    @has_permissions(administrator=True)
    async def settings(self, ctx, setting: str = None, switch=None):
        """Panel Ustawień"""
        server = self.bot.get_guild(ctx.guild.id)
        server_id = server.id
        if server_id not in cr.server_parameters:
            cr.server_parameters[server_id] = cr.GuildParameters(server_id)
        server_config = await cr.server_parameters[server_id].check_config()
        prefix = await cr.server_parameters[server_id].get_prefix()
        if setting is not None:
            setting.lower()

        async def help_menu():
            embed = discord.Embed(
                colour=discord.Colour.blue()
            )

            embed.set_author(name="Ustawienia bota KBot {} na serwerze {}".format(config.version, ctx.guild.name))
            embed.add_field(name="Wymagana rola DJ: {}".format(
                server_config["require_dj"]),
                value="{}settings dj <on/off>".format(prefix), inline=False
            )
            embed.add_field(name="Zapobieganie duplikacji pieśni w kolejce: {}".format(
                server_config["QSP"]),
                value="{}settings QSP <on/off>".format(prefix), inline=False
            )
            embed.add_field(name="Prefix: {}".format(
                prefix),
                value="{}settings prefix <nowy prefix>".format(prefix), inline=False
            )
            embed.add_field(name="Autorola: {}".format(
                server_config["autorole"]),
                value="{}settings autorole <rola do przydzielenia/brak>".format(prefix), inline=False
            )
            embed.add_field(name="Symbol waluty: {}".format(
                server_config["currency_symbol"]),
                value="{}settings curr_symbol <symbol>".format(prefix), inline=False
            )

            await ctx.send(embed=embed)

        if setting is None and switch is None:
            await help_menu()

        elif setting == "dj":
            if switch == "on":
                setting_state = ("require_dj", "on")
                await cr.server_parameters[server_id].change_config(setting_state)
                cr.server_parameters[server_id].require_dj = "on"
                await ctx.send("Wymaganie roli DJ pomyślnie włączone!")
            elif switch == "off":
                setting_state = ("require_dj", "off")
                await cr.server_parameters[server_id].change_config(setting_state)
                cr.server_parameters[server_id].require_dj = "off"
                await ctx.send("Wymaganie roli DJ pomyślnie wyłączone!")
            elif switch is None:
                embed = discord.Embed(
                    colour=discord.Colour.blue()
                )

                embed.set_author(name="Ustawienie parametru")
                embed.add_field(name="Wymagana rola DJ: {}".format(
                    server_config["require_dj"]),
                    value="{}settings dj <on/off>".format(prefix), inline=False)

                await ctx.send(embed=embed)
            else:
                await ctx.send("Nieprawidłowa wartość! Wpisz {}settings, by dowiedzieć się więcej".format(prefix))

        elif setting == "qsp":
            if switch == "on":
                setting_state = ("QSP", True)
                await cr.server_parameters[server_id].change_config(setting_state)
                await ctx.send("Zapobieganie duplikacji pieśni w kolejce pomyślnie włączone!")
            elif switch == "off":
                setting_state = ("QSP", False)
                await cr.server_parameters[server_id].change_config(setting_state)
                await ctx.send("Zapobieganie duplikacji pieśni w kolejce pomyślnie wyłączone!")
            elif switch is None:
                embed = discord.Embed(
                    colour=discord.Colour.blue()
                )

                embed.set_author(name="Ustawienie parametru")
                embed.add_field(name="Zapobieganie duplikacji pieśni w kolejce: {}".format(
                    server_config["QSP"]),
                    value="{}settings QSP <on/off>".format(prefix), inline=False)

                await ctx.send(embed=embed)
            else:
                await ctx.send("Nieprawidłowa wartość! Wpisz {}settings, by dowiedzieć się więcej".format(prefix))

        elif setting == "prefix":
            new_prefix = str(switch)
            if switch == prefix:
                await ctx.send("Już jest ustawiony taki prefix!")
            elif len(switch) > 5:
                await ctx.send("Ten prefix jest za długi! Maksymalna długość prefixu to 5 znaków!")
            elif switch is None:
                embed = discord.Embed(
                    colour=discord.Colour.blue()
                )

                embed.set_author(name="Ustawienie parametru")
                embed.add_field(name="Prefix: {}".format(
                    prefix),
                    value="{}settings prefix <nowy prefix>".format(prefix), inline=False)

                await ctx.send(embed=embed)
            else:
                await cr.server_parameters[server_id].change_prefix(ctx, new_prefix)

        elif setting == "autorole":
            # TODO: Zamiana parametru on na konkretną rolę na serwerze
            if switch == "on":
                setting_state = ("autorole", "on")
                await cr.server_parameters[server_id].change_config(setting_state)
                await ctx.send("Autorola pomyślnie ustawiona!")
            elif switch == "brak":
                setting_state = ("autorole", None)
                await cr.server_parameters[server_id].change_config(setting_state)
                await ctx.send("Autorola pomyślnie wyłączona!")
            elif switch is None:
                embed = discord.Embed(
                    colour=discord.Colour.blue()
                )

                embed.set_author(name="Ustawienie parametru")
                embed.add_field(name="Autorola: {}".format(
                    server_config["autorole"]),
                    value="{}settings autorole <rola do przydzielenia/brak>".format(prefix), inline=False)

                await ctx.send(embed=embed)
            else:
                await ctx.send("Nieprawidłowa wartość! Wpisz {}settings, by dowiedzieć się więcej".format(prefix))

        elif setting == "curr_symbol":
            if switch is not None and len(switch) <= 5:
                setting_state = ("currency_symbol", switch)
                await cr.server_parameters[server_id].change_config(setting_state)
                await ctx.send("Symbol waluty pomyślnie zmieniony!")
            elif switch is None:
                embed = discord.Embed(
                    colour=discord.Colour.blue()
                )

                embed.set_author(name="Ustawienie parametru")
                embed.add_field(name="Symbol waluty: {}".format(
                    server_config["currency_symbol"]),
                    value="{}settings curr_symbol <symbol>".format(prefix), inline=False)

                await ctx.send(embed=embed)
            else:
                # noinspection PyTypeChecker
                if len(switch) > 5:
                    await ctx.send("Symbol jest za długi!")
                else:
                    await ctx.send("Nieprawidłowa wartość! Wpisz {}settings, by dowiedzieć się więcej".format(prefix))

        else:
            await help_menu()

    @commands.command(aliases=["dodaj_role"])
    @has_permissions(manage_roles=True)
    async def add_role(self, ctx, member: discord.Member, rola: discord.Role):
        """Obdaruj użytkownika rolą"""
        role_name = rola.name
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        await member.add_roles(role)
        await ctx.send("Rola została przyznana!")

    @commands.command(aliases=["usuń_role"])
    @has_permissions(manage_roles=True)
    async def remove_role(self, ctx, member: discord.Member, rola: discord.Role):
        """Zabierz nikczemnikowi rolę"""
        role_name = rola.name
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        await member.remove_roles(role)
        await ctx.send("Rola została odebrana!")

def setup(bot):
    bot.add_cog(Administration(bot))
