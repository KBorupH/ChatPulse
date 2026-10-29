import unittest

from platforms.twitch.twitch import Twitch
    
class TestPlatforms(unittest.TestCase):
    def test_can_create_all_platforms(self):
        # Act
        twitch = Twitch()
        
        # Assert
        self.assertEqual(twitch.name.lower(), "twitch")