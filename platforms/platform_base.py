from abc import ABC, abstractmethod
from models.message import Message
from collections.abc import Iterator

class PlatformBase(ABC):
    name: str = ""
    color: str = ""
    
    def __init__(self) -> None:
        cls = type(self)
        if not cls.name:
            raise ValueError(f"{cls.__name__} must define name")
        
        if not cls.color:
            raise ValueError(f"{cls.__name__} must define color")
    
    @abstractmethod
    def read_lines(self, channel: str) -> Iterator[str]:
        pass
    
    @abstractmethod
    def parse(self, raw_line: str) -> Message | None:
        pass
    
    @abstractmethod
    def close(self) -> None:
        pass