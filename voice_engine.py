import os
import json
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from dotenv import load_dotenv
import requests
import zipfile
from ctypes import windll

load_dotenv()

class VoiceEngine:
    def __init__(self):
        self.api_key = os.getenv("ELEVEN_API_KEY")
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID", "JBFqnCBsd6RMkjVDRZzb")
        self.model_path = os.getenv("VOSK_MODEL_PATH", "models/vosk-model-small-pt-0.3")
        
        self.q = queue.Queue()
        self.model = None
        self.recognizer = None
        self.grammar = '["jarvis", "cheguei", "liberado", "pesquisar", "sobre", "abrir", "youtube", "clima", "local", "trabalho", "status", "sistema", "trancar", "reiniciar", "silêncio", "volume", "minimizar", "tudo", "downloads", "documentos", "bloco", "notas", "calculadora", "vscode", "gerenciador", "tarefas", "github", "whatsapp", "horas", "data", "foco", "relaxar", "game", "print", "limpar", "tela", "[unk]"]'
        
        self.is_listening = False
        self._ensure_model()

    def _ensure_model(self):
        if not os.path.exists(self.model_path):
            print(f"Model not found at {self.model_path}. Downloading...")
            os.makedirs("models", exist_ok=True)
            url = "https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip"
            r = requests.get(url, stream=True)
            with open("models/model.zip", "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            with zipfile.ZipFile("models/model.zip", "r") as zip_ref:
                zip_ref.extractall("models")
            os.remove("models/model.zip")
            
        self.model = Model(self.model_path)
        self.recognizer = KaldiRecognizer(self.model, 16000, self.grammar)

    def falar_stark(self, texto):
        """
        Modified: Play audio silently in the background (HEADLESS)
        using Windows Multimedia API to avoid any player windows.
        """
        print(f"JARVIS: {texto}")
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        data = {
            "text": texto,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": { "stability": 0.5, "similarity_boost": 0.8 }
        }

        try:
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 200:
                output_file = os.path.abspath("voz.mp3")
                with open(output_file, "wb") as f:
                    f.write(response.content)
                
                # Silent background playback using MCI (Headless)
                self._play_headless(output_file)
            else:
                print(f"Erro ao gerar voz: [{response.status_code}]")
        except Exception as e:
            print(f"Erro ao gerar voz: {e}")

    def _play_headless(self, file_path):
        try:
            # Using wait to ensure greeting finishes before next action if called sequentially
            cmd_open = f'open "{file_path}" type mpegvideo alias jarvis_voice'
            cmd_play = 'play jarvis_voice wait'
            cmd_close = 'close jarvis_voice'
            
            windll.winmm.mciSendStringA(cmd_open.encode(), None, 0, 0)
            windll.winmm.mciSendStringA(cmd_play.encode(), None, 0, 0)
            windll.winmm.mciSendStringA(cmd_close.encode(), None, 0, 0)
        except Exception as e:
            print(f"Erro na reprodução silenciosa: {e}")

    def listen(self, callback):
        self.is_listening = True
        def audio_callback(indata, frames, time, status):
            self.q.put(bytes(indata))

        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                               channels=1, callback=audio_callback):
            while self.is_listening:
                data = self.q.get()
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get("text", "")
                    if text:
                        callback(text)

    def stop(self):
        self.is_listening = False
