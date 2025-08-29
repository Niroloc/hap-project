import logging
import sys

from src.bot.haperych_bot import HaperychBot
from src.context.context import Context


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
        format="%(pathname)s -- %(asctime)s -- [%(levelname)s] -- \"%(message)s \"")
    context = Context()
    bot = HaperychBot(context)
    bot.run()
