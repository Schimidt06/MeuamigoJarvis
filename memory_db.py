import sqlite3
import os
from datetime import datetime
from logger import logger

_DB_PATH = os.getenv("MEMORY_DB", "jarvis_memory.db")


def _conn():
    return sqlite3.connect(_DB_PATH)


def init():
    with _conn() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                ts        TEXT    NOT NULL,
                text      TEXT    NOT NULL,
                intent    TEXT    NOT NULL,
                response  TEXT    NOT NULL
            )
        """)
    logger.debug("Memory DB inicializado em {}", _DB_PATH)


def save(text: str, intent: str, response: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with _conn() as c:
        c.execute(
            "INSERT INTO history (ts, text, intent, response) VALUES (?, ?, ?, ?)",
            (ts, text, intent, response),
        )
    logger.debug("Memória salva: intent={} text={}", intent, text)


def get_recent(n: int = 5) -> list[dict]:
    with _conn() as c:
        rows = c.execute(
            "SELECT ts, text, intent, response FROM history ORDER BY id DESC LIMIT ?",
            (n,),
        ).fetchall()
    return [{"ts": r[0], "text": r[1], "intent": r[2], "response": r[3]} for r in reversed(rows)]


def get_context(n: int = 3) -> str:
    recent = get_recent(n)
    if not recent:
        return ""
    lines = [f"[{r['ts']}] usuário: {r['text']} → intent: {r['intent']}" for r in recent]
    return "\n".join(lines)
