
import logging
from flask import Flask
from flask_socketio import SocketIO
from pathlib import Path

import config
from routes.pages import create_pages
from routes.errors import register_error_handlers

from routes.sockets import ChatSocket
from services.monitor_service import MonitorService
from services.session_service import SessionService
from services.platform_service import PlatformService
from repositories.session_repository import SessionRepository
from repositories.channel_repository import ChannelRepository
from repositories.message_repository import MessageRepository
from repositories.stats_repository import StatsRepository

logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(name)s %(levelname)s %(message)s",
                        handlers=[logging.FileHandler("system.log", encoding="utf-8"),
                                  logging.StreamHandler()])

configs = config.load_config("config.json")

app = Flask(__name__)
socketio = SocketIO(app)
chat_socket = ChatSocket("/")
socketio.on_namespace(chat_socket)

db_path = Path(configs["data_dir"], configs["sqlite_name"])

session_repo = SessionRepository(db_path)
channel_repo = ChannelRepository(db_path)
message_repo = MessageRepository(db_path)
stats_repo = StatsRepository(db_path)

platform_service = PlatformService()
monitor_service = MonitorService(configs, session_repo, channel_repo, message_repo, on_batch=chat_socket.emit_messages)
session_service = SessionService(platform_service, session_repo, stats_repo)

app.register_blueprint(create_pages(monitor_service, session_service))
register_error_handlers(app)

if __name__ == "__main__":
    #app.run(debug=True) #Changed to support socket communication
    session_repo.end_orphaned_sessions()
    socketio.run(app, debug=True, use_reloader=False)