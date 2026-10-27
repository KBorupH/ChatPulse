from abc import ABC, abstractmethod
from models.message import Message
from collections.abc import Iterator

class PlatformBase(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @abstractmethod
    def read_lines(self, channel: str) -> Iterator[str]:
        pass
    
    @abstractmethod
    def parse(self, raw_line: str) -> Message | None:
        pass
    
    @abstractmethod
    def close(self) -> None:
        pass