CREATE TABLE users IF NOT EXISTS
    (
    tg_id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT CHECK(role IN ('admin', 'user')) NOT NULL,
    pwd_hash TEXT CHECK(LENGTH(pwd_hash) = 64) NOT NULL
    );

CREATE TABLE sources IF NOT EXISTS
    (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
    );

CREATE TABLE destinations IF NOT EXISTS
    (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
    );

CREATE TABLE loans IF NOT EXISTS
    (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER,
    dest_id INTEGER,
    loan_date TEXT NOT NULL,
    amount INTEGER NOT NULL,
    expected_close_date TEXT NOT NULL,
    reward INTEGER NOT NULL,
    fact_close_date TEXT DEFAULT NULL,
    is_prolongable INTEGER DEFAULT 0,
    legend_source TEXT NOT NULL,
    comment TEXT
    );