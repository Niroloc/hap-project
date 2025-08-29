import logging
import os
import sqlite3
from datetime import date
from traceback import format_exc


class Db:
    def __init__(self, filename: str, migration_folder: str):
        logging.info(f"trying to connect to {filename} with migrations from {migration_folder}")
        self.conn = sqlite3.connect(filename)
        self.cur = self.conn.cursor()
        with open(os.path.join(migration_folder, "forward.sql"), "rt", encoding='utf-8') as f:
            queries = f.read().split(';')
        for query in queries:
            self.cur.execute(query)
        self.conn.commit()
        logging.info("Successfully connected")

    def create_loan(
            self,
            source_id: int,
            loan_date: date,
            amount: int,
            reward: int,
            expected_settle_date: date,
            legend_source_id: int,
            comment: str = None,
            previous_loan_id: int = None) -> bool:
        query = f'''
            insert into loans
            (source_id, 
            loan_date, 
            amount, 
            expected_settle_date, 
            reward, 
            legend_source_id
            {'' if comment is None else ', comment'})
            values
            (
            {source_id},
            {loan_date.strftime("%Y-%m-%d")},
            {amount},
            {reward},
            {expected_settle_date.strftime("%Y-%m-%d")},
            {legend_source_id}
            {'' if comment is None else ", " + comment}
            )
            returning id
        '''
        try:
            self.cur.execute(query)
            res = self.cur.fetchone()[0]
        except:
            logging.error("An error occurred while creating new loan")
            logging.error(format_exc())
            return False
        if previous_loan_id is not None:
            query = f'''
                update loans
                set next_loan_id = {res}
                where id = {previous_loan_id}
            '''
        self.conn.commit()
        return True

    def add_source(self, name: str) -> bool:
        query = f'''
            insert into sources
            (name)
            values
            ('{name}')
        '''
        try:
            self.cur.execute(query)
        except:
            logging.error("An error occurred while adding source")
            logging.error(format_exc())
            return False
        return True

    def add_legend_source(self, name: str):
        query = f'''
                insert into legend_sources
                (name)
                values
                ('{name}')
                '''
        try:
            self.cur.execute(query)
        except:
            logging.error("An error occurred while adding source")
            logging.error(format_exc())
            return False
        return True

    def get_sources(self) -> list[tuple[int, str]]:
        query = f'''
            select id, name
            from sources
            order by name
        '''
        self.cur.execute(query)
        return self.cur.fetchall()

    def get_legend_sources(self) -> list[tuple[int, str]]:
        query = f'''
            select id, name
            from legend_sources
            order by name
        '''
        self.cur.execute(query)
        return self.cur.fetchall()

    def get_non_settled_loans(self) -> list[tuple[int, int, str, date, date, int, int, int, str, str]]:
        query = f'''
            select 
                l.id, 
                l.source_id, 
                s.name as source_name, 
                l.loan_date, 
                l.expected_settle_date, 
                l.amount, 
                l.amount + l.reward as total,
                l.legend_source_id,
                sl.name as legend_source_name,
                comment
            from 
                loans l left join sources s on l.source_id = s.id left join legend_sources sl on sl.id = l.legend_source_id
            where
                settle_date is null
        '''
        self.cur.execute(query)
        return self.cur.fetchall()
