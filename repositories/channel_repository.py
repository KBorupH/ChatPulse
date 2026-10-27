from contextlib import closing
from repositories.base_repository import BaseRepository

_UPSERT = """
    INSERT INTO channel (platform, login)
    VALUES (?, ?)
    ON CONFLICT (platform, login) DO UPDATE SET login = excluded.login
    RETURNING id
"""

class ChannelRepository(BaseRepository):
    def get_or_create(self, platform: str, channel_login: str) -> int:
        with closing(self._connect()) as conn, conn:
            (channel_id,) = conn.execute(_UPSERT, (platform, channel_login.lower())).fetchone()
            return channel_id
            