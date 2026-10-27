from flask import Blueprint, render_template, redirect, url_for, request
from services.monitor_service import MonitorService

def create_pages(monitor_service: MonitorService) -> Blueprint:
    bp = Blueprint("pages", __name__)
    
    @bp.route("/home")
    def redirect_to_home():
        return redirect(url_for(".monitors"))

    @bp.route("/")
    def monitors():
        # fetch actively running monitors
        return render_template("monitors.html", title="ChatPulse | Monitors")

    @bp.post("/monitors")
    def start_monitor():
        channel = request.form["channel"]
        platform = request.form["platform"]
        monitor_service.start_monitor(platform, channel)
        return redirect(url_for(".monitors"))
    
    @bp.post("/monitors/<int:monitor_id>/stop")
    def stop_monitor(monitor_id: int):
        monitor_service.stop_monitor(monitor_id)
        return redirect(url_for(".monitors"))

    @bp.route("/live")
    def livechat():
        return render_template("live_chat.html", title="ChatPulse | Live Chat")

    @bp.route("/sessions")
    def sessions():
        # fetch sessions from database
        return render_template("sessions.html", title="ChatPulse | Sessions")

    @bp.route("/sessions/<int:session_id>")
    def session_details(session_id: int):
        #fetch session details with id
        session_name = "streamer"
        session_date = "26th of Oct"
        return render_template("session_details.html", title=f"ChatPulse | {session_name} {session_date}")
    
    return bp   