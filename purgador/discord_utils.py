from enum import Enum
from typing import Optional, Union
from datetime import datetime

class Timestamp(Enum):
    DEFAULT = "<t:{}>"
    SHORT_TIME = "<t:{}:t>"
    LONG_TIME = " <t:{}:T>"
    SHORT_DATE = "<t:{}:d>"
    LONG_DATE = " <t:{}:D>"
    SHORT_TIME_DATE = "<t:{}:f>"
    LONG_TIME_DATE = "<t:{}:F>"
    RELATIVE_TIME = "<t:{}:R>"


class TextFormat(Enum):
    ITALICS = "*{}*"
    BOLD = "**{}**"
    UNDERLINE = "__{}__"
    STRIKETHROUGH = "~~{}~~"
    CODE_BLOCK = "`{}`"
    TRIPLE_CODE_BLOCK = "```{}```"
    QUOTE_BLOCK = ">>> {}"
    SPOILER = "||{}||"


class TagFormat(Enum):
    DEFAULT = "<#{}>"


class EmojiFormat(Enum):
    DEFAULT = "<:{}>"
    TWEMOJI_SMALL = "\{}"  # does not support custom emojis


def timestamp(
    seconds: Optional[Union[int, float]] = None, frmt: Timestamp = Timestamp.DEFAULT
) -> str:
    if not seconds:
        dt = datetime.utcnow()
        seconds = dt.timestamp()
    return frmt.value.format(int(seconds))


def text(text: str, frmt: TextFormat) -> str:
    return frmt.value.format(text)


def tag(id: int, frmt: TagFormat = TagFormat.DEFAULT) -> str:
    return frmt.value.format(id)


def emoji(code: int, str, frmt: EmojiFormat = EmojiFormat.DEFAULT) -> str:
    return frmt.value.format(code)
