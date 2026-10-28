from dataclasses import dataclass
from datetime import datetime

@dataclass
class Session:
    id: int
    channel_id: int
    started_at: datetime    
    ended_at: datetime | None = None


    
    