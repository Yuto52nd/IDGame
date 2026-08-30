CREATE TABLE IF NOT EXISTS question_banks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bank_key TEXT NOT NULL UNIQUE,
    label TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bank_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    UNIQUE (bank_id, question),
    FOREIGN KEY (bank_id) REFERENCES question_banks (id) ON DELETE CASCADE
);
