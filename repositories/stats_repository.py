from contextlib import closing

from repositories.base_repository import BaseRepository

_TOP_CHATTERS = """
SELECT MAX(display_name) AS name, COUNT(*) AS n
FROM message
WHERE session_id = :session_id
GROUP BY user_login
ORDER BY n DESC
LIMIT 10
"""

_TOP_EMOTES = """
SELECT e.value AS name, COUNT(*) AS n
FROM message m, json_each(m.emotes) e
WHERE m.session_id = :session_id
GROUP BY name
ORDER BY n DESC
LIMIT 10
"""

_ROLES = """
SELECT CASE
           WHEN is_broadcaster THEN 'Broadcaster'
           WHEN is_mod THEN 'Mod'
           WHEN is_sub THEN 'Sub'
           ELSE 'Other'
       END AS role,
       COUNT(*) AS n
FROM message
WHERE session_id = :session_id
GROUP BY role
ORDER BY n DESC
"""

class StatsRepository(BaseRepository):
    def get_session_stats(self, session_id: int) -> dict:
        params = {"session_id": session_id}
        with closing(self._connect()) as conn:
            return {
                "top_chatters": _fetch_all(conn, _TOP_CHATTERS, params),
                "top_emotes": _fetch_all(conn, _TOP_EMOTES, params),
                "roles": _fetch_all(conn, _ROLES, params),
            }


def _fetch_all(conn, sql: str, params: dict) -> list[dict]:
    return [dict(row) for row in conn.execute(sql, params)]