import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "assets" / "katakana_dict.db"


class DictionaryDatabase:
    def __init__(self) -> None:
        self.conn = None

    # Only try create connection and return status
    def create_connection(self) -> bool:
        if not DB_PATH.exists():
            return False

        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)

        return True

    # Handles connection
    def get_connection(self) -> sqlite3.Connection | None:
        return self.conn

    # FIXME: create_connection and get_connection can be merged,
    #        since get_connection has no check for connection status,
    #        possible interlink issue can happen


database = DictionaryDatabase()
