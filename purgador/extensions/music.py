import lightbulb
import hikari
import lavaplayer
import logging
import os
import asyncio
from .. import checks
from ..discord_utils import timestamp, Timestamp
from ..utils import from_bytes
from datetime import datetime

plugin = lightbulb.Plugin("music_plugin")

lavalink = lavaplayer.LavalinkClient(
    host=os.environ["LAVALINK_SERVER"],
    port=os.environ["LAVALINK_PORT"],
    password=os.environ["LAVALINK_PASSWORD"],
)


@lavalink.listen(lavaplayer.TrackStartEvent)
async def on_track_start(event: lavaplayer.TrackStartEvent) -> None:
    logging.info(f"{event.track.title} started at {event.guild_id}")


@lavalink.listen(lavaplayer.TrackEndEvent)
async def on_track_end(event: lavaplayer.TrackEndEvent) -> None:
    logging.info(f"{event.track.title} ended at {event.guild_id} reason {event.reason}")
    node = await lavalink.get_guild_node(event.guild_id)
    if len(node.queue) == 0:
        await plugin.bot.update_voice_state(event.guild_id, None)


@lavalink.listen(lavaplayer.WebSocketClosedEvent)
async def on_web_socket_closed(event: lavaplayer.WebSocketClosedEvent) -> None:
    logging.error(f"error with websocket {event.reason}")


@plugin.listener(hikari.StartedEvent)
async def on_start(event: hikari.StartedEvent) -> None:
    lavalink.set_user_id(plugin.bot.get_me().id)
    lavalink.set_event_loop(asyncio.get_event_loop())
    lavalink.connect()


# On voice state update the bot will update the lavalink node
@plugin.listener(hikari.VoiceStateUpdateEvent)
async def voice_state_update(event: hikari.VoiceStateUpdateEvent) -> None:
    await lavalink.raw_voice_state_update(
        event.guild_id,
        event.state.user_id,
        event.state.session_id,
        event.state.channel_id,
    )


@plugin.listener(hikari.VoiceServerUpdateEvent)
async def voice_server_update(event: hikari.VoiceServerUpdateEvent) -> None:
    await lavalink.raw_voice_server_update(event.guild_id, event.endpoint, event.token)


async def _join(ctx: lightbulb.Context) -> None:
    voice_state = plugin.bot.cache.get_voice_state(ctx.guild_id, ctx.author.id)
    channel_id = voice_state.channel_id
    await ctx.bot.update_voice_state(ctx.guild_id, channel_id, self_deaf=True)
    await lavalink.wait_for_connection(ctx.guild_id)


@plugin.command()
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.command(name="lavalink", description="Lavalink server info")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def lavalink_info_command(ctx: lightbulb.Context) -> None:
    embed = hikari.Embed(title="Lavalink Server Status", color=0xF000FF)
    embed.add_field("Lavalink Shards", lavalink.num_shards)

    stats = lavalink.info
    # players stats
    embed.add_field("Playing Players", stats.playing_players)
    embed.add_field("Players", stats.players)

    # memory stats
    embed.add_field("Memory Used", from_bytes(stats.memory_used))
    embed.add_field("Free Memory", from_bytes(stats.memory_free))
    embed.add_field("Total Memory", from_bytes(stats.memory_free + stats.memory_used))

    # uptime stats
    elapsed = stats.uptime / 1000  # seconds
    current_time = datetime.utcnow().timestamp()
    started_at = current_time - elapsed
    embed.add_field("Uptime `UTC`", timestamp(started_at, Timestamp.RELATIVE_TIME))

    await ctx.respond(embed)


@plugin.command()
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option(name="id", description="guild id", required=True, type=int)
@lightbulb.command(name="destroy", description="Destroy node command")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def destroy_command(ctx: lightbulb.Context) -> None:
    await lavalink.destroy(ctx.options.id)


@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only, checks.author_in_vc)
@lightbulb.command(name="join", description="Join command")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def join_command(ctx: lightbulb.Context) -> None:
    await _join(ctx)
    await ctx.respond("BUENASS 😎")


@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only, checks.author_in_vc)
@lightbulb.option(name="query", description="query to search", required=True)
@lightbulb.command(name="play", description="Play command", aliases=["p"])
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def play_command(ctx: lightbulb.Context) -> None:
    query = ctx.options.query
    result = await lavalink.auto_search_tracks(query)
    if not result:
        await ctx.respond("Pa man no encontré nada :(")
        return
    elif isinstance(result, lavaplayer.TrackLoadFailed):
        await ctx.respond(f"ABORTEN SE ROMPIO TODO\n```{result.message}```")
        return
    elif isinstance(result, lavaplayer.PlayList):
        await lavalink.add_to_queue(ctx.guild_id, result.tracks, ctx.author.id)
        await ctx.respond(
            f"CHE CAPO ACABO DE AÑADIR {len(result.tracks)} ROLAS A LA LISTA"
        )
        return

    node = await lavalink.get_guild_node(ctx.guild_id)
    if not node:
        await _join(ctx)

    await lavalink.play(ctx.guild_id, result[0], ctx.author.id)
    await ctx.respond(f"[{result[0].title}]({result[0].uri})")


@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only, checks.author_in_vc)
@lightbulb.command(name="stop", description="Stop command")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def stop_command(ctx: lightbulb.Context) -> None:
    await lavalink.stop(ctx.guild_id)
    await ctx.respond("BUENO PARA YA ME CALLO")


@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only, checks.author_in_vc)
@lightbulb.command(name="skip", description="Skip command", aliases=["s"])
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def skip_command(ctx: lightbulb.Context) -> None:
    await lavalink.skip(ctx.guild_id)
    await ctx.respond("SKIPEAMOS NAZI 😎👊")


@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only, checks.author_in_vc)
@lightbulb.command(name="pause", description="Pause command")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def pause_command(ctx: lightbulb.Context) -> None:
    await lavalink.pause(ctx.guild_id, True)
    await ctx.respond("Ponemos pausa chavalesss")


@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only, checks.author_in_vc)
@lightbulb.command(name="resume", description="Resume command")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def resume_command(ctx: lightbulb.Context) -> None:
    await lavalink.pause(ctx.guild_id, False)
    await ctx.respond("Sacamos la pausa chavaless")


@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only, checks.author_in_vc)
@lightbulb.option(name="position", description="Position to seek", required=True)
@lightbulb.command(name="seek", description="Seek command")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def seek_command(ctx: lightbulb.Context) -> None:
    position = ctx.options.position
    await lavalink.seek(ctx.guild_id, position)
    await ctx.respond(f"Adelantamos a la mejor parte 👉 `{position}`")


@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only, checks.author_in_vc)
@lightbulb.option(
    name="vol",
    description="Volume to set",
    required=True,
    type=int,
    min_value=0,
    max_value=1000,
)
@lightbulb.command(name="volume", description="Volume command")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def volume_command(ctx: lightbulb.Context) -> None:
    volume = ctx.options.vol
    await lavalink.volume(ctx.guild_id, volume)
    await ctx.respond(f"Cambiamos el volumen a `{volume}%` chavaless")


@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only, checks.author_in_vc)
@lightbulb.command(name="queue", description="Queue command")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def queue_command(ctx: lightbulb.Context) -> None:
    node = await lavalink.get_guild_node(ctx.guild_id)
    embed = hikari.Embed(
        description="\n".join(
            [f"{n+1}- [{i.title}]({i.uri})" for n, i in enumerate(node.queue)]
        )
    )
    await ctx.respond(embed=embed)


@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only, checks.author_in_vc)
@lightbulb.command(name="np", description="Now playing command")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def np_command(ctx: lightbulb.Context) -> None:
    node = await lavalink.get_guild_node(ctx.guild_id)
    if not node or not node.queue:
        await ctx.respond("Sos tonto o k")
        return
    await ctx.respond(f"[{node.queue[0].title}]({node.queue[0].uri})")


@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only, checks.author_in_vc)
@lightbulb.command(name="repeat", description="Repeat command")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def repeat_command(ctx: lightbulb.Context) -> None:
    node = await lavalink.get_guild_node(ctx.guild_id)
    stats = False if node.repeat else True
    await lavalink.repeat(ctx.guild_id, stats)
    if stats:
        await ctx.respond("Empezamos a repetir chavaless")
        return
    await ctx.respond("Ya no repito más :(")


@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only, checks.author_in_vc)
@lightbulb.command(name="shuffle", description="Shuffle command")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def shuffle_command(ctx: lightbulb.Context) -> None:
    await lavalink.shuffle(ctx.guild_id)
    await ctx.respond("Listorti 🤙")


@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command(name="leave", description="Leave command")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def leave_command(ctx: lightbulb.Context) -> None:
    await ctx.bot.update_voice_state(ctx.guild_id, None)
    await ctx.respond("HASTA LA PROXIMAA")


@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only, checks.author_in_vc)
@lightbulb.command(name="filter", description="Filter command")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def filter_command(ctx: lightbulb.Context) -> None:
    ...


@filter_command.child()
@lightbulb.add_checks(lightbulb.guild_only, checks.author_in_vc)
@lightbulb.option(name="hz", description="Filter hz", type=float, required=True)
@lightbulb.command(name="rotation", description="Rotation subcommand")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def rotation_subcommand(ctx: lightbulb.Context) -> None:
    filters = lavaplayer.Filters()  # volume = 1
    filters.rotation(ctx.options.hz)

    await lavalink.filters(ctx.guild_id, filters)
    await ctx.respond("Enjoy 😎💪")


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(plugin)
