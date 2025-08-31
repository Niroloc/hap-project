import json
import logging
import os

from src.utils.db import Db
from src.utils.reports import Reporter


class Context:
    def __init__(self):
        self.BOT_TOKEN: str = os.getenv('BOT_TOKEN')
        self.ADMIN_ID: int = 0
        try:
            self.ADMIN_ID = int(os.getenv('ADMIN_ID', ""))
        except ValueError:
            logging.error("Cannot read admin id from env vars ADNIN_ID = '{}'".format(os.getenv('ADMIN_ID', "")))
        self.DB_FILE: str = '/data/db.db'
        self.CONFIG_FILE = '/config/config.json'
        self.MIGRATIONS_FOLDER: str = '/migrations'
        if os.getenv('ENVIRNMENT', 'dev') == 'dev':
            self.DB_FILE = f'{os.environ["HOME"]}/PycharmProjects/haperychProject/db_data/db.db'
            self.CONFIG_FILE = f'{os.environ["HOME"]}/PycharmProjects/haperychProject/config/config.json'
            self.MIGRATIONS_FOLDER = f'{os.environ["HOME"]}/PycharmProjects/haperychProject/migrations/'
        data = dict()
        if os.path.isfile(self.CONFIG_FILE):
            with open(self.CONFIG_FILE) as f:
                data = json.load(f)
        self.BUTTON_TO_ALIAS: dict[str ,str] = data.get("buttons_to_factory", dict())
        self.DEFAULT_MESSAGE_FACTORY_ALIAS = data.get("default_message_factory_alias", "payback")

        self.db: Db = Db(self.DB_FILE, self.MIGRATIONS_FOLDER)
        self.reporter: Reporter = Reporter(self.db.conn)
        self.rebuild_reporter_movements: bool = True

        self.input_mode_callback_data: str | None = None
        self.input_mode_message_alias: str | None = None