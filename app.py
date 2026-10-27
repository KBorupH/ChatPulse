
import logging
from flask import Flask
import config
from routes.api import create_api
from routes.pages import create_pages
from services.monitor_service import MonitorService
from repositories.session_repository import SessionRepository
from repositories.channel_repository import ChannelRepository
from repositories.message_repository import MessageRepository

configs = config.load_config("config.json")

session_repo = SessionRepository(configs["data_dir"] + "/" + configs["sqlite_name"])
channel_repo = ChannelRepository(configs["data_dir"] + "/" + configs["sqlite_name"])
message_repo = MessageRepository(configs["data_dir"] + "/" + configs["sqlite_name"])

monitor_service = MonitorService(configs, session_repo, channel_repo, message_repo)

app = Flask(__name__)

app.register_blueprint(create_api())
app.register_blueprint(create_pages(monitor_service))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(name)s %(levelname)s %(message)s",
                        handlers=[logging.FileHandler("system.log", encoding="utf-8"),
                                  logging.StreamHandler()])
    
    app.run(debug=True)