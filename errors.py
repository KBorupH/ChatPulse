class ChatPulseError(Exception):
    """Base for all project errors."""

class MalformedLineError(ChatPulseError):
    """Raw IRC line could not be parsed."""

    def __init__(self, line: str, reason: str):
        super().__init__(f"{reason}: {line[:80]!r}")
        self.line = line
        self.reason = reason
        
class MonitorAlreadyRunningError(ChatPulseError):
    """Monitor for platform and channel already exists"""
    
class MonitorNotRunningError(ChatPulseError):
    """A stop was recieved for a monitor already stopped"""
        
class UnsupportedPlatformError(ChatPulseError):
    """Platform isn't supported"""
    def __init__(self, platform_name: str):
            super().__init__(f"Unsupported platform: {platform_name}")
            self.platform_name = platform_name