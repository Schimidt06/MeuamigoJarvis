"""
╔══════════════════════════════════════════════════════════════╗
║                   P.I.T.O.C.O  VISION HUB                    ║
║            - STARK INTELLIGENCE & INTERFACE HQ -             ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import queue
import json
import requests
import subprocess
import time
import threading
import sys
import webbrowser
import cv2
from bs4 import BeautifulSoup
import psutil
from dotenv import load_dotenv
import sounddevice as sd
import numpy as np
from pydub import AudioSegment
from rapidfuzz import fuzz
from flask import Flask, render_template, jsonify, send_from_directory
from flask_cors import CORS

load_dotenv()

# Forçar exibição bonita de caracteres no Windows
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

os.environ["VOSK_LOG_LEVEL"] = "-1"
import vosk

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURAÇÕES E ESTADO GLOBAL
# ─────────────────────────────────────────────────────────────────────────────

URL_PORTFOLIO = "https://landing-page-schimidt.vercel.app/"
AUDIO_FILE = "ACDC - Back In Black (Official 4K Video) - ACDC (128k).wav"

UOL_KEYWORDS = ['ação', 'ações', 'mercado', 'bolsa', 'política', 'governo', 'lula', 'bolsonaro', 'juros', 'economia', 'dólar', 'haddad']

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = "JBFqnCBsd6RMkjVDRZzb" 

SAMPLE_RATE = 16000
BLOCK_SIZE = 8000

# Estado do Sistema
class PitocoState:
    is_active = False
    is_muted = False
    camera_on = False
    current_rms = 0.0
    cpu_usage = 0
    ram_usage = 0

state = PitocoState()

# Cores
CYAN   = "\033[96m"
YELLOW = "\033[93m"
GREEN  = "\033[92m"
RED    = "\033[91m"
MAGENTA= "\033[95m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

def log(tag: str, message: str, color: str = CYAN) -> None:
    ts = time.strftime("%H:%M:%S")
    print(f"{color}{BOLD}[{ts}] [{tag}]{RESET} {message}")


# ─────────────────────────────────────────────────────────────────────────────
# SERVIDOR FLASK (Interface Vision Hub)
# ─────────────────────────────────────────────────────────────────────────────

app = Flask(__name__, static_folder='ui')
CORS(app)

@app.route('/')
def index():
    return send_from_directory('ui', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('ui', path)

@app.route('/status')
def get_status():
    return jsonify({
        "audio_level": float(state.current_rms),
        "cpu": state.cpu_usage,
        "ram": state.ram_usage,
        "is_active": state.is_active,
        "is_muted": state.is_muted,
        "camera_on": state.camera_on
    })

@app.route('/toggle_mute', methods=['POST'])
def toggle_mute():
    state.is_muted = not state.is_muted
    log("HUB", f"Microfone: {'MUTADO' if state.is_muted else 'ATIVO'}", YELLOW)
    return jsonify({"is_muted": state.is_muted})

@app.route('/toggle_camera', methods=['POST'])
def toggle_camera():
    state.camera_on = not state.camera_on
    if state.camera_on:
        threading.Thread(target=camera_hud_loop, daemon=True).start()
    return jsonify({"camera_on": state.camera_on})

def start_flask():
    app.run(port=5000, debug=False, use_reloader=False)


# ─────────────────────────────────────────────────────────────────────────────
# MÓDULO DE CÂMERA (OpenCV HUD)
# ─────────────────────────────────────────────────────────────────────────────

def camera_hud_loop():
    cap = cv2.VideoCapture(0)
    log("CAMERA", "Iniciando Sensores Ópticos...", GREEN)
    
    while state.camera_on:
        ret, frame = cap.read()
        if not ret: break
        
        # Inverte e aplica cor "Iron Man"
        frame = cv2.flip(frame, 1)
        hud_color = (255, 242, 0) # Cyan-like
        
        # Desenha HUD Símbolos
        h, w, _ = frame.shape
        cv2.rectangle(frame, (50, 50), (w-50, h-50), hud_color, 1)
        cv2.line(frame, (w//2 - 20, h//2), (w//2 + 20, h//2), hud_color, 1)
        cv2.line(frame, (w//2, h//2 - 20), (w//2, h//2 + 20), hud_color, 1)
        
        cv2.putText(frame, "TARGET LOCK: CHEFE", (60, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, hud_color, 1)
        cv2.putText(frame, f"SENSORS: ONLINE | {time.strftime('%H:%M:%S')}", (60, h-70), cv2.FONT_HERSHEY_SIMPLEX, 0.4, hud_color, 1)
        
        # Filtro de cor azulado suave
        overlay = frame.copy()
        cv2.rectangle(overlay, (0,0), (w,h), (50, 20, 0), -1)
        cv2.addWeighted(overlay, 0.1, frame, 0.9, 0, frame)
        
        cv2.imshow("PITOCO VISION HUD", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            state.camera_on = False
            break
            
    cap.release()
    cv2.destroyAllWindows()
    log("CAMERA", "Sensores Ópticos Desligados.", YELLOW)


# ─────────────────────────────────────────────────────────────────────────────
# MOTOR DE ÁUDIO HIGH-QUALITY
# ─────────────────────────────────────────────────────────────────────────────

def _reproduzir_audio(segment: AudioSegment):
    try:
        samples = np.array(segment.get_array_of_samples())
        if segment.sample_width == 2:
            samples = samples.astype(np.float32) / 32768.0
        elif segment.sample_width == 4:
            samples = samples.astype(np.float32) / 2147483648.0
        if segment.channels == 2:
            samples = samples.reshape((-1, 2))
        sd.play(samples, segment.frame_rate)
        sd.wait()
    except Exception as e:
        log("AUDIO_ERR", f"Falha na reprodução: {e}", RED)

def _gerar_e_tocar_ia(texto: str):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    headers = {"Accept": "audio/mpeg", "Content-Type": "application/json", "xi-api-key": ELEVENLABS_API_KEY}
    data = {"text": texto, "model_id": "eleven_multilingual_v2", "voice_settings": {"stability": 0.65, "similarity_boost": 0.85, "use_speaker_boost": True}}
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            import io
            audio_data = io.BytesIO(response.content)
            seg = AudioSegment.from_file(audio_data, format="mp3").fade_in(100).fade_out(100)
            _reproduzir_audio(seg)
            return True
        return False
    except: return False

def falar_stark(texto: str):
    log("PITOCO", f'"{texto[:65]}..."', MAGENTA)
    _gerar_e_tocar_ia(texto)


# ─────────────────────────────────────────────────────────────────────────────
# MÓDULOS DE COMANDO
# ─────────────────────────────────────────────────────────────────────────────

def module_apresentacao():
    log("PITOCO", "PROTOCOLO DE CHEGADA: ATIVADO", YELLOW)
    
    # Inicia o Vision Hub apenas agora!
    log("HUB", "Iniciando Vision Hub no endereço local...", GREEN)
    subprocess.Popen('start chrome --app="http://127.0.0.1:5000"', shell=True)
    
    webbrowser.open(URL_PORTFOLIO) 
    
    hora = time.localtime().tm_hour
    saudacao = "Bem-vindo"
    if hora < 12: saudacao = "Bom dia"
    elif hora < 18: saudacao = "Boa tarde"
    else: saudacao = "Boa noite"
    
    falar_stark(f"{saudacao}, chefe. Sistemas Vision Hub carregados. Monitorando ambiente local.")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    music_path = os.path.join(script_dir, AUDIO_FILE)
    if os.path.isfile(music_path):
        try:
            audio = AudioSegment.from_file(music_path, format="wav")
            audio_cut = audio[2500:6500].fade_in(200).fade_out(1500)
            _reproduzir_audio(audio_cut)
        except: pass

def module_noticias():
    log("PITOCO", "VARREDURA DE SATÉLITE EM CURSO...", YELLOW)
    falar_stark("Acesseis os servidores do UOL. Vou ver o que o pessoal está aprontando hoje.")
    try:
        response = requests.get('https://www.uol.com.br/', headers={'User-Agent': 'Mozilla'})
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        titulos = [h.get_text(strip=True) for h in soup.find_all(['h2', 'h3'])][:30]
        filtradas = []
        for t in titulos:
            if len(t) > 15 and any(k in t.lower() for k in UOL_KEYWORDS):
                if t not in filtradas: filtradas.append(t)
        top = filtradas[:3]
        if top:
            falar_stark("Chefe, o caos do momento é o seguinte: " + ". ".join(top) + ".")
        else:
            falar_stark("Sem notícias relevantes agora, senhor.")
    except:
        falar_stark("Falha na interceptação de dados externos.")

# (Outros módulos mantidos conforme versão anterior)
def module_trabalho():
    falar_stark("Abrindo VS Code. Hora de criar algo genial.")
    subprocess.Popen("code .", shell=True)

def module_clima():
    try:
        loc = requests.get("https://ipinfo.io/json").json()
        lat, lon = loc['loc'].split(',')
        tempo = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true").json()['current_weather']
        falar_stark(f"Temos {int(tempo['temperature'])} graus lá fora, senhor.")
    except: falar_stark("Radar de clima offline.")

def module_pesquisa(texto: str):
    termo = texto.split("pesquisar sobre")[-1].strip()
    falar_stark(f"Vasculhando arquivos externos sobre {termo}.")
    webbrowser.open(f"https://www.google.com/search?q={termo}")


# ─────────────────────────────────────────────────────────────────────────────
# INTELIGÊNCIA E RECONHECIMENTO
# ─────────────────────────────────────────────────────────────────────────────

def encontrar_comando_similar(texto_ouvido: str):
    comandos = {
        "apresentação": module_apresentacao, "notícias": module_noticias, "noticias": module_noticias,
        "status do sistema": lambda: falar_stark("Tudo voando, senhor. Bateria, CPU e RAM em ordem."),
        "hora do trabalho": module_trabalho, "previsão do tempo": module_clima, 
        "trancar sistema": lambda: os.system("rundll32.exe user32.dll,LockWorkStation"),
        "abrir youtube": lambda: webbrowser.open("https://youtube.com"),
        "abrir whatsapp": lambda: webbrowser.open("https://web.whatsapp.com"),
        "abrir github": lambda: webbrowser.open("https://github.com"),
        "liberado": "LIBERAR"
    }
    melhor_score = 0
    melhor_comando = None
    for nome, func in comandos.items():
        score = fuzz.ratio(texto_ouvido, nome)
        if score > melhor_score:
            melhor_score = score
            melhor_comando = (nome, func)
    return melhor_comando if melhor_score > 70 else None


# ─────────────────────────────────────────────────────────────────────────────
# NÚCLEO DE ESCUTA
# ─────────────────────────────────────────────────────────────────────────────

class PitocoStateMachine:
    def __init__(self):
        log("SYS", "Sincronizando Motores PITOCO...", YELLOW)
        self.model = vosk.Model(lang="pt")
        self.recognizer = vosk.KaldiRecognizer(self.model, SAMPLE_RATE)
        self.q = queue.Queue()

    def audio_callback(self, indata, frames, time_info, status):
        # Captura volume para o Hub
        audio_data = np.frombuffer(indata, dtype='int16')
        rms = np.sqrt(np.mean(audio_data.astype(np.float32)**2))
        state.current_rms = min(rms / 3000, 1.0) # Normaliza pra 0-1
        
        if not state.is_muted:
            self.q.put(bytes(indata))

    def _process_text(self, text: str):
        text = text.lower().strip()
        if not text: return

        if not state.is_active:
             if fuzz.ratio(text, "pitoco") > 70 or "pitoco" in text:
                 state.is_active = True
                 state.active_time = time.time()
                 threading.Thread(target=falar_stark, args=("Sim, senhor?",), daemon=True).start()
             return

        if time.time() - state.active_time > 10:
             state.is_active = False
             return

        if "pesquisar sobre" in text:
            state.is_active = False
            threading.Thread(target=module_pesquisa, args=(text,), daemon=True).start()
            return

        match = encontrar_comando_similar(text)
        if match:
            nome, acao = match
            state.is_active = False
            if acao == "LIBERAR": falar_stark("Sempre aqui, senhor.")
            else: threading.Thread(target=acao, daemon=True).start()
        else:
            if len(text) > 3:
                state.active_time = time.time() 
                falar_stark("Repita senhor, não entendi.")

    def update_system_stats(self):
        while True:
            state.cpu_usage = int(psutil.cpu_percent())
            state.ram_usage = int(psutil.virtual_memory().percent)
            time.sleep(1)

    def start(self):
        # Inicia Servidor UI e Monitoramento em background
        threading.Thread(target=start_flask, daemon=True).start()
        threading.Thread(target=self.update_system_stats, daemon=True).start()
        
        log("MIC", "Captura de Voz Ativa. Aguardando gatilho 'Pitoco'...", GREEN)
        try:
            with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=BLOCK_SIZE, dtype="int16", channels=1, callback=self.audio_callback):
                while True:
                    if state.is_active and (time.time() - state.active_time > 10):
                        state.is_active = False
                    if not self.q.empty():
                        data = self.q.get()
                        if self.recognizer.AcceptWaveform(data):
                            res = json.loads(self.recognizer.Result()).get("text", "")
                            if res: 
                                log("DEBUG", f"ESCUTADO: {res}", YELLOW)
                                self._process_text(res)
                        else:
                            # Log parcial opcional para diagnóstico
                            partial = json.loads(self.recognizer.PartialResult()).get("partial", "")
                            if partial:
                                print(f"\r{CYAN}[MIC]: {partial}...{RESET}", end="", flush=True)
        except KeyboardInterrupt: sys.exit(0)

if __name__ == "__main__":
    PitocoStateMachine().start()
