import unittest
from datetime import datetime, timezone

from errors import MalformedLineError
from platforms.twitch import parser

PRIVMSG = (
    "@badge-info=;badges=moderator/1;color=#FF4500;display-name=James;emotes=25:6-10;"
    "first-msg=0;id=abc-123;mod=1;subscriber=0;tmi-sent-ts=1761650175000;user-id=42;user-type=mod "
    ":james.james@james.tmi.twitch.tv PRIVMSG #uhn :hello Kappa"
)

REPLY = (
    "@badge-info=;badges=;color=;display-name=Seamus;emotes=;first-msg=0;id=def-456;mod=0;"
    "reply-parent-display-name=james;reply-parent-msg-body=gg\\swp;reply-parent-msg-id=abc-123;"
    "reply-parent-user-id=42;reply-parent-user-login=james;subscriber=1;tmi-sent-ts=1761650176000;"
    "user-id=7;user-type= :seamus!seamus@seamus.tmi.twitch.tv PRIVMSG #uhn :@james agreed"
)

class TestParsePrivmsg(unittest.TestCase):
    def setUp(self) -> None:
        message = parser.parse(PRIVMSG)
        assert message is not None
        self.message = message
        
    def test_basic_fields(self):
        # Assert
        self.assertEqual(self.message.msg_id, "abc-123")
        self.assertEqual(self.message.user, "james")
        self.assertEqual(self.message.display_name, "James")
        self.assertEqual(self.message.text, "hello Kappa")
        self.assertEqual(self.message.raw_line, PRIVMSG)
        
    def test_timestamp_is_utc_datetime(self):
        # Arrange
        expected = datetime.fromtimestamp(1761650175000 / 1000, tz=timezone.utc)
        
        # Assert
        self.assertEqual(self.message.ts, expected)
        
    def test_correct_emote_from_text(self):
        # Assert
        self.assertEqual(self.message.emotes, ("Kappa",))
        
    def test_flags(self):
        self.assertTrue(self.message.is_mod)
        self.assertFalse(self.message.is_sub)
        self.assertIsNone(self.message.reply)
        
class TestParseReply(unittest.TestCase):
    def test_reply_fields_are_unescaped(self):
        # Arrange
        message = parser.parse(REPLY)
        
        # Act
        assert message is not None
        assert message.reply is not None
        
        # Assert
        self.assertEqual(message.reply.parent_msg_id, "abc-123")
        self.assertEqual(message.reply.parent_user, "james")
        self.assertEqual(message.reply.parent_text, "gg wp")
    
class TestParseOtherLines(unittest.TestCase):
    def test_non_privmsg_returns_none(self):
        # Arrange
        text = ":tmi.twitch.tv 366 justinfan1 #uhn :End of /NAMES list"
        
        # Act
        parsed = parser.parse(text)
        
        # Assert
        self.assertIsNone(parsed)
        
    def test_malformed_line(self):
        # Arrange
        text = "@id=1"
        
        # Assert
        with self.assertRaises(MalformedLineError):
            # Act
            parser.parse(text)