import os
import queue
import threading
import time
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel
from dotenv import load_dotenv
import requests
from ctypes import windll

load_dotenv()

# Silence detection tuning
_SILENCE_RMS       = int(os.getenv("SILENCE_RMS", 300))      # energy threshold
_SILENCE_SECS      = float(os.getenv("SILENCE_SECS", 0.9))   # silence to end utterance
_MIN_SPEECH_SECS   = float(os.getenv("MIN_SPEECH_SECS", 0.4))
_SAMPLE_RATE       = 16000
_BLOCKSIZE         = 1024


class VoiceEngine:
    def __init__(self):
        self.api_key  = os.getenv("ELEVEN_API_KEY")
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID", "JBFqnCBsd6RMkjVDRZzb")
        self.q        = queue.Queue()
        self.is_listening = False

        model_size = os.getenv("WHISPER_MODEL", "base")
        print(f"[STT] Carregando Whisper '{model_size}' (primeira vez faz download)...")
        self.whisper = WhisperModel(model_size, device="cpu", compute_type="int8")
        print("[STT] Whisper pronto.")

    # ── TTS ──────────────────────────────────────────────────────────────────

    def falar_stark(self, texto: str):
        print(f"JARVIS: {texto}")
        threading.Thread(target=self._tts_and_play, args=(texto,), daemon=True).start()

    def _tts_and_play(self, texto: str):
        output_file = os.path.abspath(f"voz_{int(time.time())}.mp3")
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key,
        }
        payload = {
            "text": texto,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.8},
        }
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=15)
            if resp.status_code == 200:
                with open(output_file, "wb") as f:
                    f.write(resp.content)
                self._play_headless(output_file)
            else:
                print(f"[TTS] Erro: {resp.status_code}")
        except Exception as e:
            print(f"[TTS] Erro: {e}")
        finally:
            if os.path.exists(output_file):
                os.remove(output_file)

    def _play_headless(self, file_path: str):
        try:
            windll.winmm.mciSendStringA(f'open "{file_path}" type mpegvideo alias jv'.encode(), None, 0, 0)
            windll.winmm.mciSendStringA(b'play jv wait', None, 0, 0)
            windll.winmm.mciSendStringA(b'close jv', None, 0, 0)
        except Exception as e:
            print(f"[TTS] Erro na reprodução: {e}")

    # ── STT ──────────────────────────────────────────────────────────────────

    def listen(self, callback):
        self.is_listening = True

        silence_frames_needed = int(_SILENCE_SECS * _SAMPLE_RATE / _BLOCKSIZE)
        min_speech_frames     = int(_MIN_SPEECH_SECS * _SAMPLE_RATE / _BLOCKSIZE)

        speech_buffer: list[np.ndarray] = []
        silence_count = 0

        def audio_callback(indata, _frames, _time, _status):
            self.q.put(indata.copy())

        with sd.InputStream(samplerate=_SAMPLE_RATE, channels=1, dtype="int16",
                            blocksize=_BLOCKSIZE, callback=audio_callback):
            print("[STT] Escutando...")
            while self.is_listening:
                try:
                    chunk = self.q.get(timeout=0.5)
                except queue.Empty:
                    continue

                rms = float(np.sqrt(np.mean(chunk.astype(np.float32) ** 2)))
                is_silent = rms < _SILENCE_RMS

                if not is_silent:
                    speech_buffer.append(chunk)
                    silence_count = 0
                elif speech_buffer:
                    silence_count += 1
                    speech_buffer.append(chunk)

                    if silence_count >= silence_frames_needed:
                        if len(speech_buffer) >= min_speech_frames:
                            self._transcribe(speech_buffer, callback)
                        speech_buffer.clear()
                        silence_count = 0

    def _transcribe(self, buffer: list[np.ndarray], callback):
        audio = np.concatenate(buffer).flatten().astype(np.float32) / 32768.0
        segments, _ = self.whisper.transcribe(
            audio,
            language="pt",
            beam_size=1,
            vad_filter=True,
        )
        text = " ".join(s.text for s in segments).strip()
        if text:
            print(f"[STT] Transcrito: {text}")
            callback(text)

    def stop(self):
        self.is_listening = False
