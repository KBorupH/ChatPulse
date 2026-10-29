import unittest
from datetime import datetime, timezone, timedelta

from models.channel import Channel
from models.stats import SessionStats
    
class TestSessionStatsModel(unittest.TestCase):
    def test_correct_duration(self):
        # Arrange
        now = datetime.now(timezone.utc)
        channel = Channel(0, "twitch", "uhn")
        session_stats = SessionStats(0, channel, 234, 145, now)
        
        # Act
        session_stats.ended_at = now + timedelta(hours=2, minutes=43)
        
        # Assert
        self.assertEqual(session_stats.duration, timedelta(hours=2, minutes=43))
        
    def test_correct_duration_format_hours_and_min(self):
        # Arrange
        now = datetime.now(timezone.utc)
        channel = Channel(0, "twitch", "uhn")
        session_stats = SessionStats(0, channel, 234, 145, now)
        
        # Act
        session_stats.ended_at = now + timedelta(hours=2, minutes=43)
        
        # Assert
        self.assertEqual(session_stats.formatted_duration, "2h 43m")
        
    def test_correct_duration_format_min(self):
        # Arrange
        now = datetime.now(timezone.utc)
        channel = Channel(0, "twitch", "uhn")
        session_stats = SessionStats(0, channel, 234, 145, now)
        
        # Act
        session_stats.ended_at = now + timedelta(minutes=43)
        
        # Assert
        self.assertEqual(session_stats.formatted_duration, "43m")