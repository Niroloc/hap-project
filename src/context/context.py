import json
import logging
import os

from aiogram.types import CallbackQuery

from src.bot.callbacks.callback_factories import CallbackFactory
from src.utils.db import Db


class Context:
    def __init__(self):
        self.BOT_TOKEN: str = os.getenv('BOT_TOKEN')
        self.ADMIN_ID: int = 0
        try:
            self.ADMIN_ID = int(os.getenv('ADMIN_ID', ""))
        except ValueError:
            logging.error("Cannot read admin id from env vars ADNIN_ID = '%s'".format(os.getenv('ADMIN_ID', "")))
        self.DB_FILE: str = '/data/db.db'
        self.db = Db(self.DB_FILE)
        self.CONFIG_FILE = '/config/config.json'
        self.MIGRATIONS_FOLDER: str = '/migrations'
        if os.getenv('ENVIRNMENT', 'dev') == 'dev':
            self.DB_FILE = '$HOME/PycharmProjects/haperychProject/db_data/db.db'
            self.CONFIG_FILE = '$HOME/PycharmProjects/haperychProject/config/config.json'
            self.MIGRATIONS_FOLDER = '$HOME/PycharmProjects/haperychProject/migrations/'
        data = dict()
        if os.path.isfile(self.CONFIG_FILE):
            with open(self.CONFIG_FILE) as f:
                data = json.load(f)
        self.BUTTON_TO_FACTORY: dict[str ,str] = data.get("buttons_to_factory", dict())
        self.DEFAULT_MESSAGE_FACTORY_ALIAS = data.get("default_message_factory_alias", "payback")

        self.input_mode_callback_query: CallbackQuery | None = None
        self.input_mode_message_alias: str | None = None