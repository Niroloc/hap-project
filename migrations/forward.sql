CREATE TABLE IF NOT EXISTS sources
    (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
    );

CREATE TABLE IF NOT EXISTS legend_sources
    (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
    )

CREATE TABLE IF NOT EXISTS loans
    (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    loan_date DATE NOT NULL,
    amount INTEGER NOT NULL,
    expected_settle_date DATE NOT NULL,
    reward INTEGER NOT NULL,
    settle_date DATE DEFAULT NULL,
    next_loan_id INTEGER DEFAULT NULL,
    legend_source_id INTEGER NOT NULL,
    comment TEXT DEFAULT NULL,
    FOREIGN KEY(source_id) REFERENCES sources(id),
    FOREIGN KEY(legend_source_id) REFERENCES legend_sources(id)
    );
