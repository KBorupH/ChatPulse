from flask import Blueprint

def create_api() -> Blueprint:
    bp = Blueprint("api", __name__, url_prefix="/api")
    
    @bp.post("/monitors")
    def start_monitor():
        return ""
    
    return bp