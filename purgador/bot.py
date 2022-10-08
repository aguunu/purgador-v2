import os
import hikari
import lightbulb

bot = lightbulb.BotApp(
    token=os.getenv("TOKEN"),
    prefix=".",
    default_enabled_guilds=int(os.getenv("DEFAULT_GUILD_ID")),
    help_slash_command=True,
    intents=hikari.Intents.ALL_UNPRIVILEGED,
)

extensions_path = os.path.join(os.path.dirname(__file__), "extensions")
bot.load_extensions_from(extensions_path)


@bot.listen(hikari.StartingEvent)
async def on_starting(event: hikari.StartingEvent) -> None:
    print("Starting")


@bot.listen(hikari.StartedEvent)
async def on_started(event: hikari.StartedEvent) -> None:
    print(f"Server online!")


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
    elif ...:
        ...
    else:
        raise exception


def run() -> None:
    if os.name != "nt":
        import uvloop

        uvloop.install()

    bot.run()
