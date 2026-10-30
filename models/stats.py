from dataclasses import dataclass
from datetime import datetime, timedelta

from models.channel import Channel

@dataclass
class SessionStats:
    id: int
    channel: Channel
    messages: int
    chatters: int
    started_at: datetime    
    platform_color: str = ""
    ended_at: datetime | None = None
    
    @property
    def channel_login(self) -> str:
        return self.channel.login
    
    @property
    def platform(self) -> str:
        return self.channel.platform
    
    @property
    def duration(self) -> timedelta | None:
        if self.ended_at is None:
            return None
        return self.ended_at - self.started_at

    @property
    def formatted_duration(self) -> str:
        if self.duration is not None:
            minutes = int(self.duration.total_seconds()) // 60
            hours, minutes = divmod(minutes, 60)
            return f"{hours}h {minutes:02}m" if hours else f"{minutes}m"
        return "Running"
    
@dataclass
class SessionDetailsStats:
    session_stats: SessionStats
    per_minute: list[dict]
    top_chatters: list[dict]
    top_emotes: list[dict]
    roles: list[dict]