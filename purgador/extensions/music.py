import lightbulb
import hikari
import lavaplayer
import logging
import os
import asyncio
from .. import checks


lavalink = lavaplayer.LavalinkClient(
    host=os.environ["LAVALINK_SERVER"],
    port=os.environ["LAVALINK_PORT"],
    password=os.environ["LAVALINK_PASSWORD"],
)


@lavalink.listen(lavaplayer.TrackStartEvent)
async def track_start_event(event: lavaplayer.TrackStartEvent) -> None:
    logging.info(f"start track: {event.track.title}")


@lavalink.listen(lavaplayer.TrackEndEvent)
async def track_end_event(event: lavaplayer.TrackEndEvent) -> None:
    logging.info(f"track end: {event.track.title}")


@lavalink.listen(lavaplayer.WebSocketClosedEvent)
async def web_socket_closed_event(event: lavaplayer.WebSocketClosedEvent) -> None:
    logging.error(f"error with websocket {event.reason}")


plugin = lightbulb.Plugin("music_plugin")


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


async def _join(ctx: lightbulb.context.Context) -> None:
    voice_state = plugin.bot.cache.get_voice_state(ctx.guild_id, ctx.author.id)
    channel_id = voice_state.channel_id
    await ctx.bot.update_voice_state(ctx.guild_id, channel_id, self_deaf=True)
    await lavalink.wait_for_connection(ctx.guild_id)


@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only, checks.author_in_vc)
@lightbulb.command(name="join", description="join voice channel")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def join_command(ctx: lightbulb.context.Context) -> None:
    await _join(ctx)
    await ctx.respond("done join vc")


@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only, checks.author_in_vc)
@lightbulb.option(name="query", description="query to search", required=True)
@lightbulb.command(name="play", description="Play command", aliases=["p"])
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def play_command(ctx: lightbulb.context.Context) -> None:
    query = ctx.options.query
    result = await lavalink.auto_search_tracks(query)
    if not result:
        await ctx.respond("not found result for your query")
        return
    elif isinstance(result, lavaplayer.TrackLoadFailed):
        await ctx.respond(f"track load failed\n```{result.message}```")
        return
    elif isinstance(result, lavaplayer.PlayList):
        await lavalink.add_to_queue(ctx.guild_id, result.tracks, ctx.author.id)
        await ctx.respond(f"added {len(result.tracks)} tracks to queue")
        return

    node = await lavalink.get_guild_node(ctx.guild_id)
    if not node:
        await _join(ctx)

    await lavalink.play(ctx.guild_id, result[0], ctx.author.id)
    await ctx.respond(f"[{result[0].title}]({result[0].uri})")


@plugin.command()
@lightbulb.command(name="stop", description="Stop command")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def stop_command(ctx: lightbulb.context.Context) -> None:
    await lavalink.stop(ctx.guild_id)
    await ctx.respond("done music stopped")


@plugin.command()
@lightbulb.command(name="skip", description="Skip command", aliases=["s"])
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def skip_command(ctx: lightbulb.context.Context) -> None:
    await lavalink.skip(ctx.guild_id)
    await ctx.respond("done music skipped")


@plugin.command()
@lightbulb.command(name="pause", description="Pause command")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def pause_command(ctx: lightbulb.context.Context) -> None:
    await lavalink.pause(ctx.guild_id, True)
    await ctx.respond("done music paused")


@plugin.command()
@lightbulb.command(name="resume", description="Resume command")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def resume_command(ctx: lightbulb.context.Context) -> None:
    await lavalink.pause(ctx.guild_id, False)
    await ctx.respond("done music resumed")


@plugin.command()
@lightbulb.option(name="position", description="Position to seek", required=True)
@lightbulb.command(name="seek", description="Seek command")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def seek_command(ctx: lightbulb.context.Context) -> None:
    position = ctx.options.position
    await lavalink.seek(ctx.guild_id, position)
    await ctx.respond(f"done seek to {position}")


@plugin.command()
@lightbulb.option(name="vol", description="Volume to set", required=True)
@lightbulb.command(name="volume", description="Volume command")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def volume_command(ctx: lightbulb.context.Context) -> None:
    volume = ctx.options.vol
    await lavalink.volume(ctx.guild_id, volume)
    await ctx.respond(f"done set volume to {volume}%")


@plugin.command()
@lightbulb.command(name="destroy", description="Destroy command")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def destroy_command(ctx: lightbulb.context.Context) -> None:
    await lavalink.destroy(ctx.guild_id)
    await ctx.respond("done destroy the bot")


@plugin.command()
@lightbulb.command(name="queue", description="Queue command")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def queue_command(ctx: lightbulb.context.Context) -> None:
    node = await lavalink.get_guild_node(ctx.guild_id)
    embed = hikari.Embed(
        description="\n".join(
            [f"{n+1}- [{i.title}]({i.uri})" for n, i in enumerate(node.queue)]
        )
    )
    await ctx.respond(embed=embed)


@plugin.command()
@lightbulb.command(name="np", description="Now playing command")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def np_command(ctx: lightbulb.context.Context) -> None:
    node = await lavalink.get_guild_node(ctx.guild_id)
    if not node or not node.queue:
        await ctx.respond("nothing playing")
        return
    await ctx.respond(f"[{node.queue[0].title}]({node.queue[0].uri})")


@plugin.command()
@lightbulb.command(name="repeat", description="Repeat command")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def repeat_command(ctx: lightbulb.context.Context) -> None:
    node = await lavalink.get_guild_node(ctx.guild_id)
    stats = False if node.repeat else True
    await lavalink.repeat(ctx.guild_id, stats)
    if stats:
        await ctx.respond("done repeat the music")
        return
    await ctx.respond("done stop repeat the music")


@plugin.command()
@lightbulb.command(name="shuffle", description="Shuffle command")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def shuffle_command(ctx: lightbulb.context.Context) -> None:
    await lavalink.shuffle(ctx.guild_id)
    await ctx.respond("done shuffle the music")


@plugin.command()
@lightbulb.command(name="leave", description="Leave command")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def leave_command(ctx: lightbulb.context.Context) -> None:
    await ctx.bot.update_voice_state(ctx.guild_id, None)
    await ctx.respond("done leave the voice channel")


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(plugin)
