from dataclasses import dataclass

@dataclass
class Channel:
    id: int
    platform: str
    login: str    