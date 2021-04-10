import logging

from linebot import LineBotApi
from linebot.exceptions import LineBotApiError
from linebot.models import TextSendMessage

from ..config import LineChannelConfig

logger = logging.getLogger(__name__)


class LineBotApiDummy:
    def __init__(self, *args, **kwargs):
        ...

    def broadcast(self, *args, **kwargs):
        ...


LINE_CHANNEL_ACCESS_TOKEN = LineChannelConfig().LINE_CHANNEL_ACCESS_TOKEN

# line_bot_api: LineBotApi

# if LINE_CHANNEL_ACCESS_TOKEN:
#     line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
# else:
#     logger.warning("Not set LINE_CHANNEL_ACCESS_TOKEN. Notification's not work.")
#     line_bot_api = LineBotApiDummy(LINE_CHANNEL_ACCESS_TOKEN)


def broadcast(*messages):
    if not LINE_CHANNEL_ACCESS_TOKEN:
        logger.warning("Not set LINE_CHANNEL_ACCESS_TOKEN. Notification's not work.")
        return

    line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

    arr = [TextSendMessage(text=msg) for msg in messages]
    try:
        line_bot_api.broadcast(messages=arr)
    except LineBotApiError as e:
        logger.critical(e)
