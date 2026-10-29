from dataclasses import dataclass, field
from datetime import datetime

class MessageReply:
    def __init__(self, parent_msg_id: str, parent_user: str, parent_text: str) -> None:
        self._parent_msg_id = parent_msg_id
        self._parent_user = parent_user
        self._parent_text = parent_text
        
    @property
    def parent_msg_id(self) -> str:
        return self._parent_msg_id
    
    @property
    def parent_user(self) -> str:
        return self._parent_user
        
    @property
    def parent_text(self) -> str:
        return self._parent_text
    
@dataclass
class Message:
    raw_line: str
    platform: str
    channel: str    # without #
    ts: datetime    # utc
    user: str
    user_id: str
    display_name: str
    text: str
    color: str | None = None
    msg_id: str | None = None
    emotes: tuple[str, ...] = ()
    emote_ids: dict[str, str] = field(default_factory=dict)
    bits: int = 0
    is_broadcaster: bool = False
    is_mod: bool = False
    is_sub: bool = False
    is_first_msg: bool = False
    is_action: bool = False
    reply: MessageReply | None = None
    badges: dict | None = None 
    