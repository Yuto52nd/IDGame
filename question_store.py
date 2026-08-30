import json
import os
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
QUESTION_DATA_PATH = BASE_DIR / "data" / "questions.json"
SCHEMA_PATH = BASE_DIR / "data" / "schema.sql"
QUESTION_DB_PATH = Path(os.environ.get("QUESTION_DB_PATH", BASE_DIR / "instance" / "questions.sqlite3"))


def _connect():
    connection = sqlite3.connect(QUESTION_DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_question_db():
    QUESTION_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with QUESTION_DATA_PATH.open(encoding="utf-8") as data_file:
        seed_data = json.load(data_file)

    with _connect() as connection:
        connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        for bank in seed_data["banks"]:
            connection.execute(
                "INSERT INTO question_banks (bank_key, label) VALUES (?, ?) "
                "ON CONFLICT(bank_key) DO UPDATE SET label = excluded.label",
                (bank["key"], bank["label"]),
            )
            bank_id = connection.execute(
                "SELECT id FROM question_banks WHERE bank_key = ?", (bank["key"],)
            ).fetchone()["id"]
            connection.executemany(
                "INSERT OR IGNORE INTO questions (bank_id, question) VALUES (?, ?)",
                [(bank_id, question) for question in bank["questions"]],
            )


def get_question_banks():
    with _connect() as connection:
        rows = connection.execute(
            "SELECT bank_key, label FROM question_banks ORDER BY id"
        ).fetchall()
    return {row["bank_key"]: {"label": row["label"]} for row in rows}


def get_questions(bank_key):
    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT questions.question
            FROM questions
            JOIN question_banks ON question_banks.id = questions.bank_id
            WHERE question_banks.bank_key = ?
            ORDER BY questions.id
            """,
            (bank_key,),
        ).fetchall()
    return [row["question"] for row in rows]


def get_questions_from_banks(bank_keys):
    """Get combined questions from multiple banks, maintaining order."""
    if not bank_keys:
        bank_keys = ["classic"]
    questions = []
    with _connect() as connection:
        for bank_key in bank_keys:
            rows = connection.execute(
                """
                SELECT questions.question
                FROM questions
                JOIN question_banks ON question_banks.id = questions.bank_id
                WHERE question_banks.bank_key = ?
                ORDER BY questions.id
                """,
                (bank_key,),
            ).fetchall()
            questions.extend([row["question"] for row in rows])
    return questions


initialize_question_db()
