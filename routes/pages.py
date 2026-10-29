from flask import Blueprint, render_template, redirect, url_for, request, abort

from services.monitor_service import MonitorService
from services.session_service import SessionService
from errors import MonitorAlreadyRunningError, MonitorNotRunningError, UnsupportedPlatformError

def create_pages(monitor_service: MonitorService, session_service: SessionService) -> Blueprint:
    bp = Blueprint("pages", __name__)
    
    @bp.route("/home")
    def redirect_to_home():
        return redirect(url_for(".monitors"))

    @bp.route("/")
    def monitors():
        return render_template("monitors.html", title="ChatPulse | Monitors", monitors=monitor_service.running(), error=request.args.get("error"))

    @bp.post("/monitors")
    def start_monitor():
        channel_login = request.form["channel_login"]
        platform = request.form["platform"]
        try:
            monitor_service.start(platform, channel_login)
        except MonitorAlreadyRunningError:
            return redirect(url_for(".monitors", error=f"#{channel_login.lower()} is already being monitored"))
        except UnsupportedPlatformError:
            return redirect(url_for(".monitors", error=f"{platform} is not supported"))
        return redirect(url_for(".monitors"))
    
    @bp.post("/monitors/<int:channel_id>/stop")
    def stop_monitor(channel_id: int):
        try:
            monitor_service.stop(channel_id)
        except MonitorNotRunningError:
            pass
        return redirect(url_for(".monitors"))

    @bp.route("/live")
    def livechat():
        return render_template("live_chat.html", title="ChatPulse | Live Chat", monitors=monitor_service.running())

    @bp.route("/sessions")
    def sessions():
        return render_template("sessions.html", title="ChatPulse | Sessions", sessions=session_service.get_all_stats())

    @bp.route("/sessions/<int:session_id>")
    def session_details(session_id: int):
        details_stats = session_service.get_details_stats(session_id)
        if not details_stats:
            abort(404)
            
        return render_template("session_details.html", title=f"ChatPulse | {details_stats.session_stats.channel.login} {details_stats.session_stats.started_at.date()}", detail=details_stats)
    
    return bp   