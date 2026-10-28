import threading, logging, time
from enum import Enum
from collections.abc import Callable

from platforms.platform_base import PlatformBase
from models.message import Message
from errors import MalformedLineError
from repositories.message_repository import MessageRepository

log = logging.getLogger(__name__)

class MonitorStatus(Enum):
    NOT_STARTED = "not started"
    RUNNING = "running"
    STOPPED = "stopped"
    FAILED = "failed"

class Monitor:
    def __init__(self, configs: dict, session_id: int, channel_id: int, channel_login: str, platform_base: PlatformBase, message_repo: MessageRepository, on_batch: Callable[[int, list[Message]], None]) -> None:
        self._configs = configs
        self._session_id = session_id
        self._channel_id = channel_id
        self._channel_login = channel_login.lower()
        self._platform_base = platform_base
        self._message_repo = message_repo
        self._on_batch = on_batch
        self._started_at: float | None = None
        self._messages: list[Message] = []
        self._status = MonitorStatus.NOT_STARTED
        self._run_thread: threading.Thread | None = None
        self._flush_thread: threading.Thread | None = None
        self._messages_lock = threading.Lock()
        self._stop_event = threading.Event()
        
    @property
    def session_id(self) -> int:
        return self._session_id
        
    @property
    def channel_login(self) -> str:
        return self._channel_login
    
    @property
    def channel_id(self) -> int:
        return self._channel_id
    
    @property
    def platform_name(self) -> str:
        return self._platform_base.name
    
    @property
    def status(self) -> str:
        return self._status.value
    
    def start(self) -> None:
        self._status = MonitorStatus.RUNNING
        self._run_thread = threading.Thread(target=self._run, daemon=True)
        self._flush_thread = threading.Thread(target=self._flush_loop, daemon=True)
        self._started_at = time.monotonic()
        self._run_thread.start()
        self._flush_thread.start()
    
    def stop(self) -> None:
        self._stop_event.set()
        self._platform_base.close()
        if self._run_thread is not None: 
            self._run_thread.join(timeout=5)
        if self._flush_thread is not None: 
            self._flush_thread.join(timeout=5)
    
    def _run(self) -> None:
        try:
            for line in self._platform_base.read_lines(self._channel_login):
                if self._stop_event.is_set():
                    return
                
                try: 
                    message = self._platform_base.parse(line)
                except MalformedLineError as e:
                    log.warning("Skipped line on #%s: %s", self._channel_login, e)
                    continue
                if message is None:
                    continue
                with self._messages_lock:
                    self._messages.append(message)
            self._status = MonitorStatus.STOPPED
        except Exception:
            log.exception("Monitor %s:%s failed", self.platform_name, self._channel_login)
        finally:
            self._stop_event.set() # stops the flush loop too
            self._status = MonitorStatus.FAILED
            
        
    
    def _flush_loop(self) -> None:
        interval = self._configs["flush_interval_ms"] / 1000
        while not self._stop_event.wait(interval):
            self._flush_once()
        self._flush_once()          # send what's left after stop
    
    def _flush_once(self) -> None:
        with self._messages_lock:
            batch, self._messages = self._messages, []
        if not batch:
            return
        
        try:
            self._message_repo.add_many(self.session_id, batch)
            self._on_batch(self._channel_id, batch) 
        except Exception:
            log.exception("Flush failed on #%s", self._channel_login)