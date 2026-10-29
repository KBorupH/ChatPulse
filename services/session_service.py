

from repositories.session_repository import SessionRepository
from repositories.stats_repository import StatsRepository

from services.platform_service import PlatformService

from models.stats import SessionStats, SessionDetailsStats

class SessionService:
    def __init__(self, platform_service: PlatformService, session_repo: SessionRepository, stats_repo: StatsRepository) -> None:
        self._platform_service = platform_service
        self._session_repo = session_repo
        self._stats_repo = stats_repo
    
    def get_all_stats(self) -> list[SessionStats]:
        sessions = self._session_repo.get_all_stats()
        for session in sessions:
            session.platform_color = self._platform_service.get_platform_color(session.channel.platform)
        return sessions
    
    def get_details_stats(self, session_id: int) -> SessionDetailsStats | None:
        session = self._session_repo.get_stats(session_id)
        if session is None:
            return None
        
        session.platform_color = self._platform_service.get_platform_color(session.channel.platform)
        
        stats = self._stats_repo.get_session_stats(session_id)
        return SessionDetailsStats(session_stats=session, **stats)
        