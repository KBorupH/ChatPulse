
from flask import Flask, render_template, request, url_for, redirect, abort
import config

configs = config.load_config("config.json")

app = Flask(__name__)

@app.route("/home")
def redirect_to_home():
    return redirect(url_for(monitors.__name__))

@app.route("/")
def monitors():
    # fetch actively running monitors
    return render_template("monitors.html", title="ChatPulse | Monitors")

@app.route("/livechat")
def livechat():
    return render_template("live_chat.html", title="ChatPulse | Live Chat")

@app.route("/sessions")
def sessions():
    # fetch sessions from database
    return render_template("sessions.html", title="ChatPulse | Sessions")

@app.route("/session_details/<int:session_id>")
def session_details(session_id: int):
    #fetch session details with id
    session_name = "streamer"
    session_date = "26th of Oct"
    return render_template("session_details.html", title=f"ChatPulse | {session_name} {session_date}")

if __name__ == "__main__":
    app.run(debug=True)