import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "assets" / "katakana_dict.db"


class DictionaryDatabase:
    def __init__(self) -> None:
        self.conn = None

    def create_connection(self) -> bool:
        if not DB_PATH.exists():
            return False

        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)

        return True

    def get_connection(self) -> sqlite3.Connection | None:
        return self.conn


database = DictionaryDatabase()
