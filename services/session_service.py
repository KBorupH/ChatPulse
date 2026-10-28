

from repositories.session_repository import SessionRepository
from repositories.stats_repository import StatsRepository

from models.stats import SessionStats, SessionDetailsStats

class SessionService:
    def __init__(self, session_repo: SessionRepository, stats_repo: StatsRepository) -> None:
        self._session_repo = session_repo
        self._stats_repo = stats_repo
    
    def get_all_stats(self) -> list[SessionStats]:
        return self._session_repo.get_all_stats()
    
    def get_details_stats(self, session_id: int) -> SessionDetailsStats | None:
        session = self._session_repo.get_stats(session_id)
        if session is None:
            return None
        
        stats = self._stats_repo.get_session_stats(session_id)
        return SessionDetailsStats(session_stats=session, **stats)
        