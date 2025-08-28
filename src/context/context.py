import json
import logging
import os

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
        if os.getenv('ENVIRNMENT', 'dev') == 'dev':
            self.DB_FILE = '$HOME/PycharmProjects/haperychProject/db_data/db.db'
            self.CONFIG_FILE = '$HOME/PycharmProjects/haperychProject/config/config.json'
        self.button_to_factory: dict[str, str] = {}
        data = dict()
        if os.path.isfile(self.CONFIG_FILE):
            with open(self.CONFIG_FILE) as f:
                data = json.load(f)
        self.button_to_factory = data.get("buttons_to_factory", dict())
        self.DEFAULT_MESSAGE_FACTORY_ALIAS = data.get("default_message_factory_alias", "payback")
