import asyncio
import os

from bot import Tg
from utils.db import Db


if __name__ == '__main__':
    DB_FILE = 'db_data/db.db'
    FORWARD_MIGRATION_FILE = 'migrations/forward.sql'
    token = os.getenv('BOT_TOKEN')
    db = Db(DB_FILE, FORWARD_MIGRATION_FILE)
    bot = Tg(token, db)
    asyncio.run(bot.run())
