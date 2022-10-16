import os
import hikari
import lightbulb
from . import exceptions

bot = lightbulb.BotApp(
    token=os.environ["TOKEN"],
    prefix=".",
    help_slash_command=True,
    intents=hikari.Intents.ALL_UNPRIVILEGED,
)

default_guilds = os.environ.get("DEFAULT_ENABLED_GUILDS")
if default_guilds:
    default_guilds = map(int, default_guilds.split(","))
    bot.default_enabled_guilds = tuple(default_guilds)


extensions_path = os.path.join(os.path.dirname(__file__), "extensions")
bot.load_extensions_from(extensions_path)


@bot.listen(hikari.StartingEvent)
async def on_starting(event: hikari.StartingEvent) -> None:
    print("Starting")


@bot.listen(hikari.StartedEvent)
async def on_started(event: hikari.StartedEvent) -> None:
    print("Server online!")


@bot.listen(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent) -> None:
    if isinstance(event.exception, lightbulb.CommandInvocationError):
        await event.context.respond(
            f"Something went wrong during invocation of command `{event.context.command.name}`."
        )
        raise event.exception

    # Unwrap the exception to get the original cause
    exception = event.exception.__cause__ or event.exception

    if isinstance(exception, lightbulb.NotOwner):
        await event.context.respond("You are not the owner of this bot.")
    elif isinstance(exception, lightbulb.CommandIsOnCooldown):
        await event.context.respond(
            f"This command is on cooldown. Retry in `{exception.retry_after:.2f}` seconds."
        )
    elif isinstance(exception, lightbulb.OnlyInGuild):
        await event.context.respond("This command can be used only in guilds.")
    elif isinstance(exception, exceptions.AuthorNotInVoiceChannel):
        await event.context.respond("You are not in a voice channel.")
    else:
        raise exception


def run() -> None:
    if os.name != "nt":
        import uvloop

        uvloop.install()

    bot.run()
