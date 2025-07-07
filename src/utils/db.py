import os
import sqlite3


class Db:
    def __init__(self, filename: str):
        tables_exist = os.path.isfile(filename)
        self.conn = sqlite3.connect(filename)
        self.cur = self.conn.cursor()
        if not tables_exist:
            with open('../migrations/forward.sql', "rt", encoding='utf-8') as f:
                queries = f.read().split(';')
            for query in queries:
                self.cur.execute(query)
                self.conn.commit()
