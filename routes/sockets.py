from flask_socketio import join_room, leave_room, Namespace
from models.message import Message

def _room(channel_id: int) -> str:
    return f"channel:{channel_id}"

def _to_payload(message: Message) -> dict:
    reply = message.reply
        
    return {
        "platform_msg_id": message.msg_id,
        "sent_at": round(message.ts.timestamp() * 1000),
        "user_login": message.user,
        "display_name": message.display_name,
        "text": message.text,
        "color": message.color,
        "emotes": list(message.emotes),
        "bits": message.bits,
        "is_broadcaster": message.is_broadcaster,
        "is_mod": message.is_mod,
        "is_sub": message.is_sub,
        "is_first_msg": message.is_first_msg,
        "is_action": message.is_action,
        "reply_to_msg_id": reply.parent_msg_id if reply else None,
        "reply_to_login": reply.parent_user if reply else None,
        "reply_to_body": reply.parent_text if reply else None,
    }

class ChatSocket(Namespace):
    def on_join(self, data):
        join_room(_room(int(data["channel_id"])))
    
    def emit_messages(self, channel_id: int, messages: list[Message]) -> None:
        self.emit(
            "messages", 
            {"channel_id": channel_id, "messages": [_to_payload(m) for m in messages]}, 
            room=_room(channel_id)
        )