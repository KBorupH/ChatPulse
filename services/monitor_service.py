from errors import UnsupportedPlatformError, MonitorAlreadyRunningError, MonitorNotRunningError
from datetime import datetime, timezone
from collections.abc import Callable
import threading

from models.message import Message
from services.monitor import Monitor
from platforms.twitch.twitch import Twitch
from platforms.platform_base import PlatformBase

from repositories.session_repository import SessionRepository
from repositories.channel_repository import ChannelRepository
from repositories.message_repository import MessageRepository

class MonitorService:
    def __init__(self, configs: dict, session_repo: SessionRepository, channel_repo: ChannelRepository, message_repo: MessageRepository, on_batch: Callable[[int, list[Message]], None]) -> None:
        self._configs = configs
        self._session_repo = session_repo
        self._channel_repo = channel_repo
        self._message_repo = message_repo
        self._on_batch = on_batch
        self._monitors: dict[int, Monitor] = {}
        self._lock = threading.Lock()
    
    def start(self, platform_name: str, channel_login: str):
        channel_login = channel_login.lower()
        platform = self._get_platform(platform_name)
        
        # with more time, a unit of work pattern would've been implemented in places like so
        channel_id = self._channel_repo.get_or_create(platform_name, channel_login)
        with self._lock:
            if channel_id in self._monitors:
                raise MonitorAlreadyRunningError()
            
            session_id = self._session_repo.create(channel_id, datetime.now(timezone.utc))
            
            self._monitors[channel_id] = Monitor(self._configs, session_id, channel_id, channel_login, platform, self._message_repo, self._on_batch)
            self._monitors[channel_id].start()
                
    
    def stop(self, channel_id: int):
        with self._lock:
            monitor = self._monitors.pop(channel_id, None)
        if monitor is None:
            raise MonitorNotRunningError()
        
        monitor.stop()
        self._session_repo.update(monitor.session_id, datetime.now(timezone.utc))
        
    def running(self) -> list[Monitor]:
        with self._lock:
            return list(self._monitors.values())
        
    def _get_platform(self, platform_name) -> PlatformBase:
        match platform_name.lower():
            case "twitch":
                return Twitch()
            case _:
                raise UnsupportedPlatformError(platform_name)