import lightbulb

plugin = lightbulb.Plugin("owner_plugin")
plugin.add_checks(lightbulb.owner_only)


@plugin.command()
@lightbulb.command(name="guilds_info", description="Get guilds info command")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def guilds_info_command(ctx: lightbulb.Context) -> None:
    guilds = ctx.bot.cache.get_guilds_view()
    await ctx.respond(f"The bot is available on {len(guilds)} guilds.")


@plugin.command()
@lightbulb.option(name="id", description="Guild to purge slash commands", required=True)
@lightbulb.command(
    name="purge_slash_commands",
    description="Purge slash commands from a specific guild (not global commands)",
)
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def purge_slash_command(ctx: lightbulb.Context) -> None:
    await ctx.bot.purge_application_commands(ctx.options.id, global_commands=False)
    await ctx.respond(f"Purge done at guild `{ctx.options.id}` ☠")

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(plugin)
