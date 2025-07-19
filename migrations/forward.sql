CREATE TABLE IF NOT EXISTS sources
    (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
    );

CREATE TABLE IF NOT EXISTS destinations
    (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
    );

CREATE TABLE IF NOT EXISTS users
    (
    tg_id INTEGER PRIMARY KEY,
    roles TEXT CHECK(roles IN ('admin', 'user')) NOT NULL,
    source_id INTEGER DEFAULT NULL,
    dest_id INTEGET DEFAULT NULL
    );

CREATE TABLE IF NOT EXISTS loans
    (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER,
    dest_id INTEGER,
    loan_date TEXT NOT NULL,
    amount INTEGER NOT NULL,
    expected_settle_date TEXT NOT NULL,
    reward INTEGER NOT NULL,
    settle_date TEXT DEFAULT NULL,
    next_loan_id INTEGER DEFAULT NULL,
    legend_source TEXT NOT NULL,
    comment TEXT DEFAULT NULL,
    FOREIGN KEY(source_id) REFERENCES sources(id),
    FOREIGN KEY(dest_id) REFERENCES destinations(id)
    );

CREATE TABLE IF NOT EXISTS positions
    (
    source_id INTEGER NOT NULL UNIQUE,
    current_position INTEGER NOT NULL,
    FOREIGN KEY(source_id) REFERENCES sources(id)
    );

CREATE TABLE IF NOT EXISTS movements
    (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    dest_id INTEGER NOT NULL,
    amount INTEGER NOT NULL,
    FOREIGN KEY(source_id) REFERENCES sources(id),
    FOREIGN KEY(dest_id) REFERENCES destinations(id)
    );
