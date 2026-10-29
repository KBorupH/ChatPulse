from platforms.twitch.twitch import Twitch
from errors import UnsupportedPlatformError

class PlatformService:
   def get_platform_color(self, platform_name: str) -> str:
       match platform_name.lower():
            case "twitch":
                return Twitch.color
            case _:
                raise UnsupportedPlatformError(platform_name)