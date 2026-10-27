import sqlite3

class BaseRepository:
    def __init__(self, db_path: str):
        self._db_path = db_path
    
    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn