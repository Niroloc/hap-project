import os.path
from sqlite3 import Connection
from datetime import date, datetime

import pandas as pd
from matplotlib import pyplot as plt


class Reporter:
    def __init__(self, db_conn: Connection):
        self.conn = db_conn
        self.movements: pd.DataFrame = pd.DataFrame(columns=["source_name", "legend_name", "date", "movement"])

    def get_movements(self) -> str:
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
        self.movements["date"] = self.movements["date"].apply(lambda x: datetime.strptime(x, "%Y-%m-%d"))
        self.movements.sort_values(by=['date'], inplace=True)

    def get_graphic_by_sources(self, year: int | None = None, month: int | None = None) -> str:
        data = self.movements[["source_name", "date", "movement"]]
        positions = data.groupby(["source_name", "date"]).sum().groupby(level=0).cumsum().reset_index()
        positions.rename(columns={"movement": "position"}, inplace=True)
        if year is not None:
            positions = positions[positions["date"].dt.year == year]
            if month is not None:
                positions = positions[positions["date"].dt.month == month]
        sources = positions["source_name"].unique()

        plt.ioff()
        plt.figure(figsize=(12, 12))
        plt.title("Проект Хапэрыч, динамика позиций реальных источников")
        for source in sources:
            view = positions[positions["source_name"] == source]
            plt.plot(view["date"], view["position"], label=source)
        plt.legend()
        plt.grid()
        tmp_folder = "/tmp"
        os.makedirs(tmp_folder, exist_ok=True)
        result_file = (f"report_by_sources_"
                       f"{'all' if year is None else year}"
                       f"{'' if month is None or year is None else '_'+str(month)}.png")
        result_file = os.path.join(tmp_folder, result_file)
        plt.savefig(result_file)
        return result_file

