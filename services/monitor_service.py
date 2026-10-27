from services.monitor import Monitor
from platforms.twitch.twitch import Twitch
from errors import UnsupportedPlatformError, MonitorAlreadyExists, MonitorAlreadyStopped
from datetime import datetime, timezone

from repositories.session_repository import SessionRepository
from repositories.channel_repository import ChannelRepository
from repositories.message_repository import MessageRepository

class MonitorService:
    def __init__(self, configs: dict, session_repo: SessionRepository, channel_repo: ChannelRepository, message_repo: MessageRepository) -> None:
        self._configs = configs
        self._session_repo = session_repo
        self._channel_repo = channel_repo
        self._message_repo = message_repo
        self._monitors: dict[int, Monitor] = {}
    
    def start(self, platform_name: str, channel_login: str):
        match platform_name:
            case "twitch":
                platform = Twitch()
            case _:
                raise UnsupportedPlatformError(platform_name)
        
        # with more time, a unit of work pattern would've been implemented in places like so
        channel_id = self._channel_repo.get_or_create(platform_name, channel_login)
        
        if channel_id in self._monitors:
            raise MonitorAlreadyExists()
        
        session_id = self._session_repo.create(channel_id, datetime.now(timezone.utc))
        
        self._monitors[channel_id] = Monitor(self._configs, session_id, self._message_repo)
        self._monitors[channel_id].start(channel_login, platform)
                
    
    def stop(self, channel_id: int):
        monitor = self._monitors.pop(channel_id, None)
        if monitor is None:
            raise MonitorAlreadyStopped()
        
        monitor.stop()
        self._session_repo.update(monitor.session_id, datetime.now(timezone.utc))