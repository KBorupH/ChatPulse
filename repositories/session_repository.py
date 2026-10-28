from contextlib import closing
from datetime import datetime, timezone

from repositories.base_repository import BaseRepository

from models.channel import Channel
from models.stats import SessionStats

_SELECT_ALL_STATS = """
SELECT s.id, c.id as channel_id, c.login AS channel_login, c.platform, s.started_at, s.ended_at,
       COUNT(m.id) AS messages,
       COUNT(DISTINCT m.user_login) AS chatters
FROM session s
JOIN channel c ON c.id = s.channel_id
LEFT JOIN message m ON m.session_id = s.id
GROUP BY s.id
ORDER BY s.started_at DESC
"""

_SELECT_ONE_STATS = """
SELECT s.id, c.id as channel_id, c.login AS channel_login, c.platform, s.started_at, s.ended_at,
       COUNT(m.id) AS messages,
       COUNT(DISTINCT m.user_login) AS chatters
FROM session s
JOIN channel c ON c.id = s.channel_id
LEFT JOIN message m ON m.session_id = s.id
WHERE s.id = :session_id
GROUP BY s.id
"""

_INSERT = """
INSERT INTO session(channel_id, started_at) VALUES (:channel_id, :started_at) RETURNING id
"""

_UPDATE = """
UPDATE session SET ended_at = :ended_at WHERE id = :session_id
"""

_END_SESSIONS = """
UPDATE session
SET ended_at = COALESCE(
    (SELECT MAX(sent_at) FROM message WHERE message.session_id = session.id),
    started_at
)
WHERE ended_at IS NULL;
"""

def _to_session_stats(row: dict) -> SessionStats:
    channel = Channel(row["channel_id"], row["platform"], row["channel_login"])
    return SessionStats(id = row["id"], 
                        channel = channel, 
                        messages = row["messages"], 
                        chatters = row["chatters"], 
                        started_at=datetime.fromtimestamp(row["started_at"] / 1000, tz=timezone.utc), 
                        ended_at=(datetime.fromtimestamp(row["ended_at"] / 1000, tz=timezone.utc)
                            if row["ended_at"] is not None else None))

class SessionRepository(BaseRepository):
    def create(self, channel_id: int, started_at: datetime) -> int:
        """Time is received as datetime but stored in epoch ms"""
        with closing(self._connect()) as conn, conn:
            (session_id,) = conn.execute(_INSERT, {"channel_id": channel_id, "started_at": round(started_at.timestamp() * 1000)}).fetchone()
            return session_id
    
    def update(self, session_id: int, ended_at: datetime) -> None:
        """Time is received as datetime but stored in epoch ms"""
        with closing(self._connect()) as conn, conn:
            conn.execute(_UPDATE, {"session_id": session_id, "ended_at": round(ended_at.timestamp() * 1000)})
            
    def get_all_stats(self) -> list[SessionStats]:
        with closing(self._connect()) as conn:
            return [_to_session_stats(row) for row in conn.execute(_SELECT_ALL_STATS).fetchall()]
        
    def get_stats(self, session_id: int) -> SessionStats | None:
        with closing(self._connect()) as conn:
            row = conn.execute(_SELECT_ONE_STATS, {"session_id": session_id}).fetchone()
        return _to_session_stats(row) if row else None
    
    def end_orphaned_sessions(self) -> None:
        with closing(self._connect()) as conn, conn:
            conn.execute(_END_SESSIONS)