import logging
import socket
import threading
import time
from collections import deque
from collections.abc import Iterator

from decorators import retry
from models.message import Message
from ..platform_base import PlatformBase
from . import parser

log = logging.getLogger(__name__)

SERVER = "irc.chat.twitch.tv"
PORT = 6667
NICK = "justinfan12345"  # anonymous read-only login
READ_TIMEOUT = 360  # Twitch pings about every 5 minutes

class Twitch(PlatformBase):
    name: str = "twitch"
    color: str = "#A970FF"
    
    def __init__(self, reconnect_delay: float = 5, max_reconnects_per_hour: int = 10 ) -> None:
        super().__init__()
        self._reconnect_delay = reconnect_delay
        self._max_reconnects = max_reconnects_per_hour
        self._reconnects: deque[float] = deque()
        self._sock: socket.socket | None = None
        self._closed = threading.Event()
        
    def read_lines(self, channel: str) -> Iterator[str]:
        channel = channel.lower()

        while not self._closed.is_set():
            log.info("Connecting to #%s", channel)
            try:
                sock = self._connect(channel)
            except OSError:
                log.error("Could not connect to #%s, giving up", channel)
                return

            self._sock = sock
            try:
                with sock:
                    for line in sock.makefile(
                        "r", encoding="utf-8", errors="replace", newline="\r\n"
                    ):
                        line = line.rstrip("\r\n")
                        if not line:
                            continue
                        if line.startswith("PING"):
                            sock.sendall(f"PONG{line[4:]}\r\n".encode())
                            continue
                        # 366 = end of the names list, Twitch's confirmation that the join worked
                        if line.startswith(":") and line.split(" ", 2)[1:2] == ["366"]:
                            log.info("Joined #%s", channel)
                        yield line
            except OSError as e:
                if not self._closed.is_set():
                    log.warning("Connection to #%s lost: %s", channel, e)
            finally:
                self._sock = None

            if self._closed.is_set():
                break

            log.info("Disconnected from #%s", channel)
            self._reconnects.append(time.monotonic())
            if self._reconnects_last_hour() > self._max_reconnects:
                log.error("Too many reconnects for #%s, giving up", channel)
                break
            self._closed.wait(self._reconnect_delay)

        log.info("Stopped reading #%s", channel)

    def parse(self, raw_line: str) -> Message | None:
        return parser.parse(raw_line)

    def close(self) -> None:
        self._closed.set()
        sock = self._sock
        if sock is not None:
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass

    @retry()
    def _connect(self, channel: str) -> socket.socket:
        sock = socket.create_connection((SERVER, PORT), timeout=10)
        try:
            sock.sendall(b"CAP REQ :twitch.tv/tags twitch.tv/commands\r\n")
            sock.sendall(f"NICK {NICK}\r\n".encode())
            sock.sendall(f"JOIN #{channel}\r\n".encode())
            sock.settimeout(READ_TIMEOUT)
        except OSError:
            sock.close()
            raise
        return sock

    def _reconnects_last_hour(self) -> int:
        now = time.monotonic()
        while self._reconnects and now - self._reconnects[0] > 3600:
            self._reconnects.popleft()
        return len(self._reconnects)
