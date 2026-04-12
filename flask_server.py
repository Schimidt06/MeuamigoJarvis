from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import psutil
import threading
import time
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'jarvis_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    landing_url = os.getenv("LANDING_PAGE_URL", "https://landing-page-schimidt.vercel.app/")
    return render_template('index.html', landing_url=landing_url)

def system_stats_thread():
    while True:
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        battery = psutil.sensors_battery()
        battery_pct = battery.percent if battery else 100
        
        socketio.emit('stats_update', {
            'cpu': cpu,
            'ram': ram,
            'battery': battery_pct
        })
        time.sleep(2)

def start_server():
    port = int(os.getenv("HUD_PORT", 5000))
    # Start stats thread
    t = threading.Thread(target=system_stats_thread, daemon=True)
    t.start()
    socketio.run(app, port=port, debug=False)

if __name__ == '__main__':
    start_server()
