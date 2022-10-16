import lightbulb
from . import exceptions


def _author_in_vc(context: lightbulb.Context) -> bool:
    voice_state = context.bot.cache.get_voice_state(context.guild_id, context.author.id)
    if not voice_state:
        raise exceptions.AuthorNotInVoiceChannel
    return voice_state


author_in_vc = lightbulb.Check(_author_in_vc)
"""Prevents a command from being used if the user is not in a voice channel."""
