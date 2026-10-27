from contextlib import closing
from repositories.base_repository import BaseRepository
from datetime import datetime

_INSERT = """
INSERT INTO session(channel_id, started_at) VALUES (?, ?) RETURNING id
"""

_UPDATE = """
UPDATE session SET ended_at = ? WHERE id = ?
"""

class SessionRepository(BaseRepository):
    def create(self, channel_id: int, started_at: datetime) -> int:
        """Time is recieved as datetime but stored in epoch ms"""
        with closing(self._connect()) as conn, conn:
            (session_id,) = conn.execute(_INSERT, (channel_id, round(started_at.timestamp() * 1000))).fetchone()
            return session_id
    
    def update(self, session_id: int, ended_at: datetime) -> None:
        """Time is recieved as datetime but stored in epoch ms"""
        with closing(self._connect()) as conn, conn:
            conn.execute(_UPDATE, (round(ended_at.timestamp() * 1000), session_id))