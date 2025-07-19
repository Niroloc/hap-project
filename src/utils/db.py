import os
import sqlite3
from typing import Union
from enum import Enum


class ROLE(Enum):
    NOT_USER = 0
    USER = 1
    ADMIN = 2


class Db:
    def __init__(self, filename: str, forward_migration: str, author_id: int):
        tables_exist = os.path.isfile(filename)
        self.conn = sqlite3.connect(filename)
        self.cur = self.conn.cursor()
        self.mp = {'admin': 2, 'user': 1}
        if not tables_exist:
            with open(forward_migration, "rt", encoding='utf-8') as f:
                queries = f.read().split(';')
            for query in queries:
                self.cur.execute(query)
                self.conn.commit()
        self.cur.execute(f'SELECT roles FROM users WHERE tg_id={author_id}')
        roles = self.cur.fetchall()
        if len(roles) == 0:
            self.add_user(author_id, 'admin')
        elif roles[0][0] != 'admin':
            self.cur.execute(f"UPDATE users SET roles='admin' WHERE tg_id = {author_id}")

    def user_role(self, tg_id: Union[str, int]) -> ROLE:
        query = f'SELECT roles FROM users WHERE tg_id = {tg_id}'
        self.cur.execute(query)
        res = self.cur.fetchall()
        if len(res) == 0:
            return ROLE(0)
        return ROLE(self.mp.get(res[0][0]))
    
    def source_exists(self, source_id: int) -> bool:
        if not isinstance(source_id):
            return False
        self.cur.execute(f"SELECT 1 fROM sources WHERE id = {source_id}")
        return len(self.cur.fetchall()) >= 1
    
    def dest_exists(self, dest_id: int) -> bool:
        if not isinstance(dest_id):
            return False
        self.cur.execute(f"SELECT 1 fROM destinations WHERE id = {dest_id}")
        return len(self.cur.fetchall()) >= 1
    
    def add_user(self, tg_id: int, role: str = 'user', source_id: int = None, dest_id: int = None) -> None:
        if role not in self.mp:
            role = 'user'
        self.cur.execute(f'''
                            INSERT INTO users(tg_id, roles)
                            VALUES ({tg_id}, '{role}')
                            ON CONFLICT(tg_id) DO UPDATE SET
                            roles = '{role}'
                            WHERE tg_id = {tg_id}
                            ''')
        if self.source_exists(source_id):
            self.cur.execute(f'''
                                UPDATE users
                                SET source_id = {source_id}
                                ''')
        if self.dest_exists(dest_id):
            self.cur.execute(f'''
                                UPDATE users
                                SET dest_id = {dest_id}
                                ''')
        self.conn.commit()
