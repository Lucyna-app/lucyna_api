import sqlite3
from contextlib import contextmanager
import os

# Join the directory of (folder one level outside of current file) with ("lucyna.db")
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "lucyna.db")


@contextmanager
def sqlite_connection():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    with sqlite_connection() as con:
        cur = con.cursor()
        cur.executescript("""
        CREATE TABLE IF NOT EXISTS "border" (
            "uuid4" TEXT NOT NULL UNIQUE,
            "name" TEXT NOT NULL,
            "rarity" INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS "character_alias" (
            "uuid4" INTEGER PRIMARY KEY AUTOINCREMENT,
            "character_uuid4" TEXT NOT NULL,
            "alias" TEXT NOT NULL,
            "language" TEXT NOT NULL,
            FOREIGN KEY("character_uuid4") REFERENCES "character"("uuid4")
        );

        CREATE TABLE IF NOT EXISTS "user" (
            "discord_id" TEXT PRIMARY KEY,
            "last_drop_time" DATETIME,
            "drop_count" INTEGER,
            "claim_count" INTEGER,
            "vote_count" INTEGER,
            "daily_count" INTEGER,
            "favorite_series_uuid4" TEXT,
            "favorite_card_uuid4" TEXT
        );

        CREATE TABLE IF NOT EXISTS "character" (
            "uuid4" TEXT PRIMARY KEY,
            "name" TEXT NOT NULL,
            "series_uuid4" TEXT NOT NULL,
            "rarity" INTEGER NOT NULL,
            FOREIGN KEY("series_uuid4") REFERENCES "series"("uuid4")
        );

        CREATE TABLE IF NOT EXISTS "art" (
            "uuid4" TEXT PRIMARY KEY,
            "character_uuid4" TEXT NOT NULL,
            FOREIGN KEY("character_uuid4") REFERENCES "character"("uuid4")
        );

        CREATE TABLE IF NOT EXISTS "series_alias" (
            "uuid4" INTEGER PRIMARY KEY AUTOINCREMENT,
            "series_uuid4" TEXT NOT NULL,
            "alias" TEXT NOT NULL,
            "language" TEXT NOT NULL,
            FOREIGN KEY("series_uuid4") REFERENCES "series"("uuid4")
        );

        CREATE TABLE IF NOT EXISTS "configuration" (
            "discord_id" TEXT PRIMARY KEY,
            FOREIGN KEY("discord_id") REFERENCES "user"("discord_id")
        );

        CREATE TABLE IF NOT EXISTS "series" (
            "uuid4" TEXT PRIMARY KEY,
            "name" TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS "cards" (
            "uuid4" TEXT PRIMARY KEY,
            "discord_id" TEXT NOT NULL,
            "custom_code" TEXT,
            "character_uuid4" TEXT NOT NULL,
            "series_uuid4" TEXT NOT NULL,
            "art_uuid4" TEXT NOT NULL,
            "border_uuid4" TEXT NOT NULL,
            "tag" TEXT,
            "claim_time" DATETIME NOT NULL,
            FOREIGN KEY("border_uuid4") REFERENCES "border"("uuid4"),
            FOREIGN KEY("discord_id") REFERENCES "user"("discord_id"),
            FOREIGN KEY("character_uuid4") REFERENCES "character"("uuid4"),
            FOREIGN KEY("art_uuid4") REFERENCES "art"("uuid4"),
            FOREIGN KEY("series_uuid4") REFERENCES "series"("uuid4")
        );""")
