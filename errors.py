class ChatAnalyticsError(Exception):
    """Base for all project errors."""

class MalformedLineError(ChatAnalyticsError):
    """Raw IRC line could not be parsed."""

    def __init__(self, line: str, reason: str):
        super().__init__(f"{reason}: {line[:80]!r}")
        self.line = line
        self.reason = reason