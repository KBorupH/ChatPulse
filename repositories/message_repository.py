from contextlib import closing
from repositories.base_repository import BaseRepository
from models.message import Message

_INSERT = """
INSERT INTO message (
    session_id, platform_msg_id, sent_at,
    user_login, user_id, display_name,
    text, emotes, bits,
    is_broadcaster, is_mod, is_sub, is_first_msg, is_action,
    reply_to_msg_id, reply_to_login, reply_to_body,
    raw_line
)
VALUES (
    
)
ON CONFLICT (platform_msg_id) DO NOTHING
""" # TODO: Finish value with named placeholders

class MessageRepository(BaseRepository):
    def add_many(self, session_id: int, messages: list[Message]) -> None:
        if not messages:
            return
        
        with closing(self._connect()) as conn, conn:
            conn.executemany(_INSERT, messages) # TODO: Convert messages to a dict, list comprehension?
        
    