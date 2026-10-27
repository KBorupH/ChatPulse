from platforms.platform_base import PlatformBase
from models.message import Message
import threading, logging, time
from enum import Enum
from errors import MalformedLineError
from repositories.message_repository import MessageRepository

log = logging.getLogger(__name__)

class MonitorStatus(Enum):
    NOT_STARTED = "not started"
    RUNNING = "running"
    STOPPED = "stopped"

class Monitor:
    def __init__(self, configs: dict, session_id: int, message_repo: MessageRepository) -> None:
        self._configs = configs
        self._session_id = session_id
        self._message_repo = message_repo
        self._channel_login: str | None = None
        self._platform_base: PlatformBase | None = None
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
    def channel_login(self) -> str | None:
        return self._channel_login
    
    @property
    def platform(self) -> str | None:
        return self._platform_base.name if self._platform_base is not None else None
    
    def start(self, channel_login: str, platform_base: PlatformBase) -> None:
        self._channel_login = channel_login
        self._platform_base = platform_base
        self._status = MonitorStatus.RUNNING
        self._run_thread = threading.Thread(target=self._run, args=(channel_login, platform_base), daemon=True)
        self._flush_thread = threading.Thread(target=self._flush_loop, daemon=True)
        self._started_at = time.monotonic()
        self._run_thread.start()
        self._flush_thread.start()
    
    def stop(self) -> None:
        self._stop_event.set()
        if self._platform_base is not None:
            self._platform_base.close()
        if self._run_thread is not None: 
            self._run_thread.join(timeout=5)
        if self._flush_thread is not None: 
            self._flush_thread.join(timeout=5)
    
    def _run(self, channel: str, platform_base: PlatformBase) -> None:
        try:
            for line in platform_base.read_lines(channel):
                if self._stop_event.is_set():
                    return
                
                try: 
                    message = platform_base.parse(line)
                except MalformedLineError as e:
                    log.warning("Skipped line on #%s: %s", self._channel_login, e)
                    continue
                if message is None:
                    continue
                with self._messages_lock:
                    self._messages.append(message)
        except Exception:
            platform_name = self.platform
            log.exception("Monitor %s:%s failed", self._channel_login, platform_name)
        finally:
            self._stop_event.set() # stops the flush loop too
            self._status = MonitorStatus.STOPPED
            
        
    
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
        
        
        # write batch to the database, then socket update it