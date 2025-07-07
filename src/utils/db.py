import os
import sqlite3


class Db:
    def __init__(self, filename: str):
        tables_exist = os.path.isfile(filename)
        self.conn = sqlite3.connect(filename)
        self.cur = self.conn.cursor()