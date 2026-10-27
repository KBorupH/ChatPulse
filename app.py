
import logging
from flask import Flask
import config
from routes.api import create_api
from routes.pages import create_pages
from services.monitor_service import MonitorService

configs = config.load_config("config.json")


monitor_service = MonitorService()

app = Flask(__name__)

app.register_blueprint(create_api())
app.register_blueprint(create_pages(monitor_service))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(name)s %(levelname)s %(message)s",
                        handlers=[logging.FileHandler("system.log", encoding="utf-8"),
                                  logging.StreamHandler()])
    
    app.run(debug=True)