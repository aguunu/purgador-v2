import hikari
import lightbulb

plugin = lightbulb.Plugin("adminPlugin")


# @plugin.command
# @lightbulb.add_checks(lightbulb.owner_only)
# @lightbulb.command(...)
# @lightbulb.implements(...)
# async def foo(ctx):
#     ...


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(plugin)
