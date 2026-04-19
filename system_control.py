import os
import subprocess
import psutil
import ctypes
import time
import pyautogui
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

class SystemControl:
    @staticmethod
    def lock_windows():
        ctypes.windll.user32.LockWorkStation()

    @staticmethod
    def set_volume(level):
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)
        volume.SetMasterVolumeLevelScalar(level / 100, None)

    @staticmethod
    def get_volume():
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)
        return int(volume.GetMasterVolumeLevelScalar() * 100)

    @staticmethod
    def change_volume(delta):
        current = SystemControl.get_volume()
        new_vol = max(0, min(100, current + delta))
        SystemControl.set_volume(new_vol)
        return new_vol

    @staticmethod
    def mute_system():
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)
        volume.SetMute(1, None)

    @staticmethod
    def get_system_stats():
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        battery = psutil.sensors_battery()
        battery_pct = battery.percent if battery else "N/A"
        return {
            "cpu": cpu,
            "ram": ram,
            "battery": battery_pct
        }

    @staticmethod
    def open_app(path_or_command):
        try:
            os.startfile(path_or_command)
        except:
            subprocess.Popen(path_or_command, shell=True)

    @staticmethod
    def restart_system():
        os.system("shutdown /r /t 1")

    @staticmethod
    def minimize_all():
        pyautogui.hotkey('win', 'd')

    @staticmethod
    def take_screenshot():
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        pyautogui.screenshot(filename)
        return filename

    @staticmethod
    def open_folder(folder_name):
        user_path = os.path.expanduser("~")
        paths = {
            "downloads": os.path.join(user_path, "Downloads"),
            "documentos": os.path.join(user_path, "Documents"),
            "área de trabalho": os.path.join(user_path, "Desktop")
        }
        if folder_name.lower() in paths:
            os.startfile(paths[folder_name.lower()])

    @staticmethod
    def play_greeting_music():
        try:
            import numpy as np
            from pydub import AudioSegment
            import sounddevice as sd
            import io

            # Load the AC/DC file specifically mentioned
            song_path = r"ACDC - Back In Black (Official 4K Video) - ACDC (128k).wav"
            if os.path.exists(song_path):
                song = AudioSegment.from_file(song_path)
                
                # Extract seconds 2 to 6 (2000ms to 6000ms)
                snippet = song[2000:6000]
                
                # Convert to numpy array
                samples = np.array(snippet.get_array_of_samples()).astype(np.float32)
                
                # Normalize and handle channels
                if snippet.sample_width == 2: samples /= 32768.0
                if snippet.channels > 1: samples = samples.reshape((-1, snippet.channels))
                
                # Play headlessly
                sd.play(samples, snippet.frame_rate)
                # We don't sd.wait() here to let JARVIS speak over the music
        except Exception as e:
            print(f"Erro ao tocar trilha de ativação: {e}")

    @staticmethod
    def open_professional_window(url):
        """
        Opens a URL in a professional, standalone 'Kiosk Mode' (Full Screen).
        Removes all browser UI (tabs, bars, buttons) for a cinematic experience.
        """
        try:
            # Using Edge with --kiosk flag for absolute full-screen
            # --edge-kiosk-type=fullscreen ensures it uses the entire monitor
            command = f'start msedge --kiosk "{url}" --edge-kiosk-type=fullscreen'
            subprocess.Popen(command, shell=True)
        except Exception as e:
            print(f"Erro ao abrir janela profissional: {e}")
            # Fallback to standard browser if something goes wrong
            import webbrowser
            webbrowser.open(url)

    @staticmethod
    def close_all_apps():
        # Optional: Close non-essential apps for Game Mode
        apps_to_close = ["chrome", "discord", "spotify", "code"]
        for proc in psutil.process_iter(['name']):
            if any(app in proc.info['name'].lower() for app in apps_to_close):
                try:
                    proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
