import lightbulb
import hikari
import lavaplayer
import logging
import os
import asyncio

plugin = lightbulb.Plugin("music_plugin")

lavalink = lavaplayer.LavalinkClient(
    host=os.getenv("LAVALINK_SERVER"),  # Lavalink host
    port=os.getenv("LAVALINK_PORT"),  # Lavalink port
    password=os.getenv("LAVALINK_PASSWORD"),  # Lavalink password
)


@plugin.listener(hikari.StartedEvent)
async def on_start(event: hikari.StartedEvent):
    lavalink.set_user_id(plugin.bot.get_me().id)
    lavalink.set_event_loop(asyncio.get_event_loop())
    lavalink.connect()


# On voice state update the bot will update the lavalink node
@plugin.listener(hikari.VoiceStateUpdateEvent)
async def voice_state_update(event: hikari.VoiceStateUpdateEvent):
    await lavalink.raw_voice_state_update(
        event.guild_id,
        event.state.user_id,
        event.state.session_id,
        event.state.channel_id,
    )


@plugin.listener(hikari.VoiceServerUpdateEvent)
async def voice_server_update(event: hikari.VoiceServerUpdateEvent):
    await lavalink.raw_voice_server_update(event.guild_id, event.endpoint, event.token)


# Commands
# ------------------------------------- #
@plugin.command()
@lightbulb.command(name="join", description="join voice channel")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def join_command(ctx: lightbulb.context.Context):
    states = plugin.bot.cache.get_voice_states_view_for_guild(ctx.guild_id)
    voice_state = [
        state
        async for state in states.iterator().filter(
            lambda i: i.user_id == ctx.author.id
        )
    ]
    if not voice_state:
        await ctx.respond("you are not in a voice channel")
        return
    channel_id = voice_state[0].channel_id
    await plugin.bot.update_voice_state(ctx.guild_id, channel_id, self_deaf=True)
    await lavalink.wait_for_connection(ctx.guild_id)
    await ctx.respond(f"done join to <#{channel_id}>")


@plugin.command()
@lightbulb.option(name="query", description="query to search", required=True)
@lightbulb.command(name="play", description="Play command", aliases=["p"])
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def play_command(ctx: lightbulb.context.Context):
    query = ctx.options.query  # get query from options
    result = await lavalink.auto_search_tracks(query)  # search for the query
    if not result:
        await ctx.respond("not found result for your query")
        return
    elif isinstance(result, lavaplayer.TrackLoadFailed):
        await ctx.respond(f"Track load failed.\n```{result.message}```")
        return
    elif isinstance(result, lavaplayer.PlayList):
        await lavalink.add_to_queue(ctx.guild_id, result.tracks, ctx.author.id)
        await ctx.respond(f"added {len(result.tracks)} tracks to queue")
        return

    await lavalink.play(ctx.guild_id, result[0], ctx.author.id)  # play the first result
    await ctx.respond(f"[{result[0].title}]({result[0].uri})")  # send the embed


@plugin.command()
@lightbulb.command(name="stop", description="Stop command", aliases=["s"])
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def stop_command(ctx: lightbulb.context.Context):
    await lavalink.stop(ctx.guild_id)
    await ctx.respond("done stop the music")


@plugin.command()
@lightbulb.command(name="pause", description="Pause command")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def pause_command(ctx: lightbulb.context.Context):
    await lavalink.pause(ctx.guild_id, True)
    await ctx.respond("The music is paused now")


@plugin.command()
@lightbulb.command(name="resume", description="Resume command")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def resume_command(ctx: lightbulb.context.Context):
    await lavalink.pause(ctx.guild_id, False)
    await ctx.respond("The music is resumed now")


@plugin.command()
@lightbulb.option(name="position", description="Position to seek", required=True)
@lightbulb.command(name="seek", description="Seek command")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def seek_command(ctx: lightbulb.context.Context):
    position = ctx.options.position
    await lavalink.seek(ctx.guild_id, position)
    await ctx.respond(f"done seek to {position}")


@plugin.command()
@lightbulb.option(name="vol", description="Volume to set", required=True)
@lightbulb.command(name="volume", description="Volume command")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def volume_command(ctx: lightbulb.context.Context):
    volume = ctx.options.vol
    await lavalink.volume(ctx.guild_id, volume)
    await ctx.respond(f"done set volume to {volume}%")


@plugin.command()
@lightbulb.command(name="destroy", description="Destroy command")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def destroy_command(ctx: lightbulb.context.Context):
    await lavalink.destroy(ctx.guild_id)
    await ctx.respond("done destroy the bot")


@plugin.command()
@lightbulb.command(name="queue", description="Queue command")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def queue_command(ctx: lightbulb.context.Context):
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
async def np_command(ctx: lightbulb.context.Context):
    node = await lavalink.get_guild_node(ctx.guild_id)
    if not node or not node.queue:
        await ctx.respond("nothing playing")
        return
    await ctx.respond(f"[{node.queue[0].title}]({node.queue[0].uri})")


@plugin.command()
@lightbulb.command(name="repeat", description="Repeat command")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def repeat_command(ctx: lightbulb.context.Context):
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
async def shuffle_command(ctx: lightbulb.context.Context):
    await lavalink.shuffle(ctx.guild_id)
    await ctx.respond("done shuffle the music")


@plugin.command()
@lightbulb.command(name="leave", description="Leave command")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def leave_command(ctx: lightbulb.context.Context):
    await plugin.bot.update_voice_state(ctx.guild_id, None)
    await ctx.respond("done leave the voice channel")


# ------------------------------------- #


@lavalink.listen(lavaplayer.TrackStartEvent)
async def track_start_event(event: lavaplayer.TrackStartEvent):
    logging.info(f"start track: {event.track.title}")


@lavalink.listen(lavaplayer.TrackEndEvent)
async def track_end_event(event: lavaplayer.TrackEndEvent):
    logging.info(f"track end: {event.track.title}")


@lavalink.listen(lavaplayer.WebSocketClosedEvent)
async def web_socket_closed_event(event: lavaplayer.WebSocketClosedEvent):
    logging.error(f"error with websocket {event.reason}")


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(plugin)
