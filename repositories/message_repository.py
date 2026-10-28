from contextlib import closing
import json

from models.message import Message
from repositories.base_repository import BaseRepository

_INSERT = """
INSERT INTO message (
    session_id, platform_msg_id, sent_at,
    user_login, user_id, display_name,
    text, color, emotes, bits,
    is_broadcaster, is_mod, is_sub, is_first_msg, is_action,
    reply_to_msg_id, reply_to_login, reply_to_body,
    raw_line
)
VALUES (
    :session_id, :platform_msg_id, :sent_at,
    :user_login, :user_id, :display_name,
    :text, :color, :emotes, :bits,
    :is_broadcaster, :is_mod, :is_sub, :is_first_msg, :is_action,
    :reply_to_msg_id, :reply_to_login, :reply_to_body,
    :raw_line
)
ON CONFLICT (platform_msg_id) DO NOTHING
"""

def _to_row(session_id: int, message: Message) -> dict:
    reply = message.reply
    
    return {
        "session_id": session_id,
        "platform_msg_id": message.msg_id,
        "sent_at": round(message.ts.timestamp() * 1000),
        "user_login": message.user,
        "user_id": message.user_id,
        "display_name": message.display_name,
        "text": message.text,
        "color": message.color,
        "emotes": json.dumps(message.emotes),
        "bits": message.bits,
        "is_broadcaster": message.is_broadcaster,
        "is_mod": message.is_mod,
        "is_sub": message.is_sub,
        "is_first_msg": message.is_first_msg,
        "is_action": message.is_action,
        "reply_to_msg_id": reply.parent_msg_id if reply else None,
        "reply_to_login": reply.parent_user if reply else None,
        "reply_to_body": reply.parent_text if reply else None,
        "raw_line": message.raw_line,
    }

class MessageRepository(BaseRepository):
    def add_many(self, session_id: int, messages: list[Message]) -> None:
        if not messages:
            return
        
        with closing(self._connect()) as conn, conn:
            conn.executemany(_INSERT, (_to_row(session_id, msg) for msg in messages))
        
    