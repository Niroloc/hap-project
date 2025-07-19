import logging
import asyncio
import os
import sys

from bot import Tg
from utils.db import Db


if __name__ == '__main__':
    logging.basicConfig(
        stream=sys.stdout,
        format='[%(asctime)s : %(name)s : %(levelname)s] -- "%(message)s"',
        datefmt="%Y-%m-%d %H-%M-%S",
        level=os.getenv('LOGLEVEL', "INFO")
    )
    DB_FILE = 'db_data/db.db'
    FORWARD_MIGRATION_FILE = 'migrations/forward.sql'
    author_id = os.getenv('AUTHOR_ID')
    token = os.getenv('BOT_TOKEN')
    logging.info("Initializing db")
    db = Db(DB_FILE, FORWARD_MIGRATION_FILE, author_id)
    logging.info("Initializing bot")
    bot = Tg(token, db)
    logging.info("Starting bot")
    asyncio.run(bot.run())
