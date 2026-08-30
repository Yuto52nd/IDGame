# Ranking Game

## Question database

Question banks are seeded from `data/questions.json` into SQLite using `data/schema.sql` when the app starts. The database is created at `instance/questions.sqlite3` by default. Set `QUESTION_DB_PATH` to use a different database location.

Run the app with:

```text
python app.py
```
