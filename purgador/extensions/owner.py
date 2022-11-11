import lightbulb

plugin = lightbulb.Plugin("owner_plugin")
plugin.add_checks(lightbulb.owner_only)


@plugin.command()
@lightbulb.command(name="guilds_info", description="Get guilds info command")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def guilds_info_command(ctx: lightbulb.Context) -> None:
    guilds = ctx.bot.cache.get_guilds_view()
    await ctx.respond(f"The bot is available on {len(guilds)} guilds.")


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(plugin)
