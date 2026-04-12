import os
import threading
import time
import webbrowser
from datetime import datetime, timedelta
from voice_engine import VoiceEngine
from command_handler import CommandHandler
from flask_server import start_server
from dotenv import load_dotenv

load_dotenv()

class JarvisSystem:
    def __init__(self):
        self.ve = VoiceEngine()
        self.ch = CommandHandler(self.ve)
        self.last_active_time = datetime.now()
        self.active_timeout = int(os.getenv("ACTIVE_TIMEOUT", 20))
        self.hud_url = f"http://localhost:{os.getenv('HUD_PORT', 5000)}"
        
        self.is_running = True

    def monitor_timeout(self):
        while self.is_running:
            if self.ch.is_active:
                if datetime.now() > self.ch.last_command_time + timedelta(seconds=self.active_timeout):
                    print("Active mode timeout. Returning to passive mode.")
                    self.ch.is_active = False
            time.sleep(1)

    def on_voice_command(self, text):
        self.ch.handle(text)
        
        if self.ch.is_active and not hasattr(self, '_hud_opened'):
            self.open_hud()
            self._hud_opened = True
        
        if not self.ch.is_active and hasattr(self, '_hud_opened'):
            delattr(self, '_hud_opened')

    def open_hud(self):
        print("Opening HUD...")
        try:
            webbrowser.open(self.hud_url)
        except Exception as e:
            print(f"Error opening HUD: {e}")

    def start(self):
        # 1. Start Flask
        flask_thread = threading.Thread(target=start_server, daemon=True)
        flask_thread.start()
        print("HUD Server started.")

        # 2. Start Timeout Monitor
        timeout_thread = threading.Thread(target=self.monitor_timeout, daemon=True)
        timeout_thread.start()

        # 3. JARVIS starts silently (No startup greeting as requested)
        print("JARVIS is listening (Passive Mode)...")
        try:
            self.ve.listen(self.on_voice_command)
        except KeyboardInterrupt:
            self.is_running = False
            print("Shutting down...")

if __name__ == "__main__":
    jarvis = JarvisSystem()
    jarvis.start()
