import os
import sqlite3
from typing import Union
from enum import Enum


class ROLE(Enum):
    NOT_USER = 0
    USER = 1
    ADMIN = 2


class Db:
    def __init__(self, filename: str, forward_migration: str):
        tables_exist = os.path.isfile(filename)
        self.conn = sqlite3.connect(filename)
        self.cur = self.conn.cursor()
        if not tables_exist:
            with open(forward_migration, "rt", encoding='utf-8') as f:
                queries = f.read().split(';')
            for query in queries:
                self.cur.execute(query)
                self.conn.commit()

    def user_role(self, tg_id: Union[str, int]) -> ROLE:
        query = f'SELECT roles FROM users WHERE tg_id = {tg_id}'
        self.cur.execute(query)
        res = self.cur.fetchall()
        mp = {'admin': 2, 'user': 1}
        if len(res) == 0:
            return ROLE(0)
        return ROLE(mp.get(res[0][0]))
