import hikari
import lightbulb

plugin = lightbulb.Plugin("music_plugin")


@plugin.command
@lightbulb.command("jjoin", "Join current voice channel.")
@lightbulb.implements(lightbulb.SlashCommand)
async def join_command(ctx: lightbulb.SlashContext):
    guild = ctx.get_guild()
    user_voice = guild.get_voice_state(ctx.user)

    if not user_voice:
        # TODO: Intentar con ephemeral
        await ctx.respond("Conectate a un canal de voz!")
        return

    voice_channel = user_voice.channel_id
    # TODO: Intentar con ephemeral
    await ctx.bot.update_voice_state(guild, voice_channel)
    await ctx.respond("Conectado!")


@plugin.command
@lightbulb.command("lleave", "Leave current voice channel.")
@lightbulb.implements(lightbulb.SlashCommand)
async def leave_command(ctx: lightbulb.SlashContext):
    guild = ctx.get_guild()

    voice_state = ctx.bot.cache.get_voice_states_view_for_guild(guild)

    if not voice_state:
        ctx.respond("Conectate a un canal de voz!")
        return

    await ctx.bot.voice.disconnect(guild)
    await ctx.respond("Desconectado!")


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(plugin)
