from flask import Flask, render_template, request
from werkzeug.exceptions import HTTPException
import logging

log = logging.getLogger(__name__)

def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(HTTPException)
    def http_error(e: HTTPException):
        code = e.code or 500
        log.warning("%s %s: %s", code, request.path, e.description)
        return render_template("error.html", title=f"ChatPulse | {code}", code=code, message=e.description), code

    @app.errorhandler(500)
    def server_error(e):
        log.warning("%s %s: %s", e.code, request.path, e.description)
        return render_template("error.html", title="ChatPulse | Error", code=500,
                               message="Something went wrong. The error has been logged."), 500
        
    @app.errorhandler(404)
    def page_not_found_error(e):
        return render_template("error.html", title="ChatPulse | Error", code=404,
                               message="The page doesn't exist D:"), 404