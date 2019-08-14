# Zgodne z KBot 0.12-x
import discord

async def user(self, ctx, user_ext_info: discord.Member):
    roles = [role for role in user_ext_info.roles]

    embed = discord.Embed(
        colour = discord.Colour.blue()
    )

    embed.set_author(name="Informacje o użytkowniku")
    embed.set_thumbnail(url=user_ext_info.avatar_url)
    embed.add_field(name="Nick and discriminator:", value="{}#{}".format(user_ext_info.name, user_ext_info.discriminator), inline=False)
    embed.add_field(name="ID:", value=user_ext_info.id, inline=False)
    embed.add_field(name="Stworzył konto na Discordzie:", value=user_ext_info.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))
    embed.add_field(name="Dołączył na serwer:", value=user_ext_info.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"), inline=False)
    embed.add_field(name="Role ({}):".format(len(roles)), value="".join([role.mention for role in roles]), inline=False)
    embed.add_field(name="Najwyższa rola", value=user_ext_info.top_role.mention, inline=False)
    embed.set_footer(text="Prośba o dane od {}".format(ctx.author), icon_url=ctx.author.avatar_url)
    await ctx.send(embed=embed)