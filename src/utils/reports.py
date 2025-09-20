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
        loans = df[["source_name", "legend_name", "loan_date", "amount", "total"]].copy()
        loans["amount"] *= -1
        loans = loans.rename(columns={"loan_date": "date", "amount": "movement", "total": "duty"})
        paybacks = df[df["settle_date"].notna()][["source_name", "legend_name", "settle_date", "total"]]
        paybacks["duty"] = -paybacks["total"]
        paybacks = paybacks.rename(columns={"settle_date": "date", "total": "movement"})
        self.movements = pd.concat([loans, paybacks])
        self.movements["date"] = self.movements["date"].apply(lambda x: datetime.strptime(x, "%Y-%m-%d"))
        self.movements.sort_values(by=['date'], inplace=True)

    def get_graphic_by_sources(self, source_id: str = 'source_name', year: int | None = None, month: int | None = None) -> list[str]:
        data = self.movements[[source_id, "date", "movement", "duty"]]
        data = data.rename(columns={source_id: "source"})
        positions = data.groupby(["source", "date"]).sum().groupby(level=0).cumsum().reset_index()
        positions.rename(columns={"movement": "position"}, inplace=True)
        if year is not None:
            positions = positions[positions["date"].dt.year == year]
            if month is not None:
                positions = positions[positions["date"].dt.month == month]
        sources = positions["source"].unique()

        plt.ioff()
        result_files: list[str] = []
        for i, source in enumerate(sources):
            plt.figure(figsize=(12, 12))
            plt.title(f"Проект Хапэрыч, динамика позиций источнику: {source}"
                      f"({'реальный' if source_id == 'source_name' else 'легенда'})")
            view = positions[positions["source"] == source]
            plt.plot(view["date"], view["position"], label=source)
            plt.plot(view["date"], view["duty"] + view["position"],
                     label=f'{source} - ожидаемая доходность',
                     linestyle='--')
            plt.legend()
            plt.grid()
            tmp_folder = "./tmp"
            os.makedirs(tmp_folder, exist_ok=True)
            result_file = (f"report_by_{source_id}_{i}_"
                           f"{'all' if year is None else year}"
                           f"{'' if month is None or year is None else '_'+str(month)}.png")
            result_file = os.path.join(tmp_folder, result_file)
            plt.savefig(result_file)
            result_files.append(result_file)

        return result_files

