from sqlite3 import Connection

import pandas as pd
import numpy as np
from matplotlib import pyplot as plt


class Reporter:
    def __init__(self, db_conn: Connection):
        self.conn = db_conn
        self.movements: pd.DataFrame = pd.DataFrame(columns=["source_name", "legend_name", "date", "movement"])

    def get_movements(self) -> None:
        query = f'''
            select
                s.name as source_name,
                sl.name as legend_name,
                l.loan_date,
                l.settle_date,
                l.amount,
                l.amount + l.reward as total
            from loans l 
                left join sources s on l.source_id = s.id 
                left join legend_sources sl on sl.id = l.legend_source_id
        '''
        df = pd.read_sql(query, self.conn)
        loans = df[["source_name", "legend_name", "loan_date", "amount"]].copy()
        loans["amount"] *= -1
        loans = loans.rename(columns={"loan_date": "date", "amount": "movement"})
        paybacks = df[df["settle_date"].notna()][["source_name", "legend_name", "settle_date", "total"]]
        paybacks = paybacks.rename(columns={"settle_date": "date", "total": "movement"})
        self.movements = pd.concat([loans, paybacks])
        self.movements.sort_values(by=['date'], inplace=True)

    def get_graphic_by_sources(self, year: int | None = None, month: int | None = None):
        data = self.movements[["source_name", "date", "movement"]]
        positions = data.groupby(["source_name", "date"]).sum().groupby(level=0).cumsum().reset_index()
        return positions
