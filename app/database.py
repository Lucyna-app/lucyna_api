import sqlite3
from dotenv import load_dotenv
from contextlib import contextmanager
import os

load_dotenv()


DB_LOCATION = os.getenv("DB_LOCATION")


@contextmanager
def sqlite_connection():
    conn = sqlite3.connect(DB_LOCATION)
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    with sqlite_connection() as con:
        cur = con.cursor()
        cur.executescript("""
        CREATE TABLE IF NOT EXISTS "border" (
            "uuid" TEXT NOT NULL UNIQUE,
            "name" TEXT NOT NULL,
            "rarity" INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS "character_alias" (
            "id" INTEGER PRIMARY KEY AUTOINCREMENT,
            "character_id" TEXT NOT NULL,
            "alias" TEXT NOT NULL,
            "language" TEXT NOT NULL,
            FOREIGN KEY("character_id") REFERENCES "character"("uuid")
        );

        CREATE TABLE IF NOT EXISTS "user" (
            "discord_id" TEXT PRIMARY KEY,
            "last_drop_time" DATETIME,
            "drop_count" INTEGER,
            "claim_count" INTEGER,
            "vote_count" INTEGER,
            "daily_count" INTEGER,
            "favorite_series" TEXT,
            "favorite_card" TEXT
        );

        CREATE TABLE IF NOT EXISTS "character" (
            "uuid" TEXT PRIMARY KEY,
            "name" TEXT NOT NULL,
            "series" TEXT NOT NULL,
            "rarity" INTEGER NOT NULL,
            FOREIGN KEY("series") REFERENCES "series"("uuid")
        );

        CREATE TABLE IF NOT EXISTS "art" (
            "uuid" TEXT PRIMARY KEY,
            "character" TEXT NOT NULL,
            "series" TEXT NOT NULL,
            FOREIGN KEY("character") REFERENCES "character"("uuid"),
            FOREIGN KEY("series") REFERENCES "series"("uuid")
        );

        CREATE TABLE IF NOT EXISTS "series_alias" (
            "id" INTEGER PRIMARY KEY AUTOINCREMENT,
            "series_id" TEXT NOT NULL,
            "alias" TEXT NOT NULL,
            "language" TEXT NOT NULL,
            FOREIGN KEY("series_id") REFERENCES "series"("uuid")
        );

        CREATE TABLE IF NOT EXISTS "configuration" (
            "discord_id" TEXT PRIMARY KEY,
            FOREIGN KEY("discord_id") REFERENCES "user"("discord_id")
        );

        CREATE TABLE IF NOT EXISTS "series" (
            "uuid" TEXT PRIMARY KEY,
            "name" TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS "cards" (
            "uuid" TEXT PRIMARY KEY,
            "discord_id" TEXT NOT NULL,
            "custom_code" TEXT,
            "character" TEXT NOT NULL,
            "series" TEXT NOT NULL,
            "art" TEXT NOT NULL,
            "border" TEXT NOT NULL,
            "tag" TEXT,
            "claim_time" DATETIME NOT NULL,
            FOREIGN KEY("border") REFERENCES "border"("uuid"),
            FOREIGN KEY("discord_id") REFERENCES "user"("discord_id"),
            FOREIGN KEY("character") REFERENCES "character"("uuid"),
            FOREIGN KEY("art") REFERENCES "art"("uuid"),
            FOREIGN KEY("series") REFERENCES "series"("uuid")
        );""")
