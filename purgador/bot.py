import os
import hikari
import lightbulb
from . import exceptions

bot = lightbulb.BotApp(
    token=os.environ["TOKEN"],
    help_slash_command=False,
    intents=hikari.Intents.ALL_UNPRIVILEGED,
)

default_guilds = os.environ.get("DEFAULT_ENABLED_GUILDS")
if default_guilds:
    default_guilds = map(int, default_guilds.split(":"))
    bot.default_enabled_guilds = tuple(default_guilds)


# load extensions from /extensions
extensions_path = os.path.join(os.path.dirname(__file__), "extensions")
bot.load_extensions_from(extensions_path)


@bot.listen(hikari.GuildJoinEvent)
async def on_guild_join(event: hikari.GuildJoinEvent) -> None:
    # TODO: Change bot default role color to 0xf000ff
    ...


@bot.listen(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent) -> None:
    if isinstance(event.exception, lightbulb.CommandInvocationError):
        await event.context.respond(f"Ripeo el bot `{event.context.command.name}`.")
        raise event.exception

    # Unwrap the exception to get the original cause
    exception = event.exception.__cause__ or event.exception

    if isinstance(exception, lightbulb.NotOwner):
        await event.context.respond("Tenes que ser el creador para usar esto crack.")
    elif isinstance(exception, lightbulb.CommandIsOnCooldown):
        await event.context.respond(f"Espera `{exception.retry_after:.2f}s` maquina.")
    elif isinstance(exception, lightbulb.OnlyInGuild):
        await event.context.respond("Anda a un server para usar este comando.")
    elif isinstance(exception, exceptions.AuthorNotInVoiceChannel):
        await event.context.respond("Entra a un canal de voz pib@.")
    else:
        raise exception


def run() -> None:
    if os.name != "nt":
        import uvloop

        uvloop.install()

    bot.run(
        status=hikari.Status.DO_NOT_DISTURB,
        activity=hikari.Activity(
            name="Made in Plata o Plomo 😎", type=hikari.ActivityType.LISTENING
        ),
    )
