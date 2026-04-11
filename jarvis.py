"""
╔══════════════════════════════════════════════════════════════╗
║                   J.A.R.V.I.S  PROTOTYPE                     ║
║            - TWO-STAGE STATE MACHINE EDITION -               ║
╚══════════════════════════════════════════════════════════════╝
"""

import sounddevice as sd
import webbrowser
import time
import threading
import sys
import os
import queue
import json
import requests
import subprocess
from bs4 import BeautifulSoup
import winsound
import psutil
from dotenv import load_dotenv

load_dotenv()

# Forçar exibição bonita de caracteres no Windows
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

os.environ["VOSK_LOG_LEVEL"] = "-1"
import vosk

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURAÇÕES
# ─────────────────────────────────────────────────────────────────────────────

URL = "https://landing-page-schimidt.vercel.app/"
AUDIO_FILE = "ACDC - Back In Black (Official 4K Video) - ACDC (128k).wav"

UOL_KEYWORDS = ['ação', 'ações', 'mercado', 'bolsa', 'política', 'governo', 'lula', 'bolsonaro', 'juros', 'economia', 'dólar', 'haddad']

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = "JBFqnCBsd6RMkjVDRZzb" 

SAMPLE_RATE = 16000
BLOCK_SIZE = 8000

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
# GERAÇÃO DE VOZ ELEVENLABS E CACHE OFFLINE
# ─────────────────────────────────────────────────────────────────────────────

VOICE_AGUARDE_FILE = "voz_aguarde.mp3"
VOICE_DIA = "voz_dia.mp3"
VOICE_TARDE = "voz_tarde.mp3"
VOICE_NOITE = "voz_noite.mp3"

TEXTO_AGUARDE = "Acessando os servidores da U O L. Buscando atualizações sobre política e mercado financeiro. Um momento."
TEXTO_DIA = "Bom dia, chefe! Sistemas autorizados e sincronizados. Preparando ambiente de apresentação."
TEXTO_TARDE = "Boa tarde, chefe! Sistemas autorizados e sincronizados. Preparando ambiente de apresentação."
TEXTO_NOITE = "Boa noite, chefe! Sistemas autorizados e sincronizados. Preparando ambiente de apresentação."

SAUDACOES_RAPIDAS = [
    "Pois não, senhor?",
    "Ao seu dispor, meu chefe.",
    "Sistemas na escuta. O que o senhor deseja?",
    "Diga as ordens, meu poderoso."
]
VOICE_ATENDIMENTO_FILES = [f"voz_atendimento_{i}.mp3" for i in range(len(SAUDACOES_RAPIDAS))]

def _gerar_voz_elevenlabs(texto: str, filepath: str) -> bool:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    data = {"text": texto, "model_id": "eleven_multilingual_v2", "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}}
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk: f.write(chunk)
            return True
        return False
    except: return False

def _pre_generate_voice() -> None:
    log("SYS", "Conectando ao núcleo da ElevenLabs. Sintetizando matrizes offline...", YELLOW)
    # Gera os blocos principais para não ter atraso
    if not os.path.exists(VOICE_DIA): _gerar_voz_elevenlabs(TEXTO_DIA, VOICE_DIA)
    if not os.path.exists(VOICE_TARDE): _gerar_voz_elevenlabs(TEXTO_TARDE, VOICE_TARDE)
    if not os.path.exists(VOICE_NOITE): _gerar_voz_elevenlabs(TEXTO_NOITE, VOICE_NOITE)
    if not os.path.exists(VOICE_AGUARDE_FILE): _gerar_voz_elevenlabs(TEXTO_AGUARDE, VOICE_AGUARDE_FILE)
    
    for i, s in enumerate(SAUDACOES_RAPIDAS):
        if not os.path.exists(VOICE_ATENDIMENTO_FILES[i]):
            _gerar_voz_elevenlabs(s, VOICE_ATENDIMENTO_FILES[i])
    log("SYS", "🗣️ Matrizes prontas e injetadas no Hardware!", GREEN)

def _play_audio_file(path: str) -> None:
    try:
        import playsound
        playsound.playsound(path)
    except: pass

def falar_dinamico(texto: str) -> None:
    log("VOICE", f'Falando: "{texto[:60]}..."', MAGENTA)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tmp_path = os.path.join(script_dir, f"voz_temp_{int(time.time()*100)}.mp3")
    
    if _gerar_voz_elevenlabs(texto, tmp_path):
        _play_audio_file(tmp_path)
    
    try: os.remove(tmp_path)
    except: pass


# ─────────────────────────────────────────────────────────────────────────────
# MÓDULOS DE COMANDO
# ─────────────────────────────────────────────────────────────────────────────

def tocar_musica() -> None:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    music_path = os.path.join(script_dir, AUDIO_FILE)
    if os.path.isfile(music_path):
        log("MUSIC", "🎵 Soltando som com Fade-Out...", GREEN)
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(music_path, format="wav")
            audio_cut = audio[2500:6000].fade_out(1500)
            tmp_musica = os.path.join(script_dir, f"temp_m_{int(time.time())}.wav")
            audio_cut.export(tmp_musica, format="wav")
            winsound.PlaySound(tmp_musica, winsound.SND_FILENAME)
            os.remove(tmp_musica)
        except Exception as e: 
            log("MUSIC", f"Erro: {e}", RED)

def module_apresentacao() -> None:
    log("JARVIS", "MODO APRESENTAÇÃO: INICIADO", YELLOW)
    try: subprocess.Popen(f'start chrome --app="{URL}" --kiosk', shell=True)
    except: webbrowser.open(URL)
    
    hora = time.localtime().tm_hour
    log("JARVIS", f"Calculando fuso horário (Hora atual: {hora}h)", "\033[90m")
    
    if hora < 12:
        _play_audio_file(VOICE_DIA)
    elif hora < 18:
        _play_audio_file(VOICE_TARDE)
    else:
        _play_audio_file(VOICE_NOITE)
    
    time.sleep(0.5)
    tocar_musica()

def module_noticias() -> None:
    log("JARVIS", "MODO RADAR: UOL", YELLOW)
    _play_audio_file(VOICE_AGUARDE_FILE)
    try:
        response = requests.get('https://www.uol.com.br/', headers={'User-Agent': 'Mozilla'})
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        titulos = [h.get_text(strip=True) for h in soup.find_all(['h2', 'h3'])]
        filtradas = []
        for t in titulos:
            if len(t) > 15 and any(k in t.lower() for k in UOL_KEYWORDS):
                if t not in filtradas: filtradas.append(t)
        
        top = filtradas[:3]
        if top:
            texto = "Chefe, as principais do momento: " + ". ".join(top) + "."
            falar_dinamico(texto)
        else:
            falar_dinamico("O radar está limpo. Sem grandes alertas.")
    except:
        falar_dinamico("Sem comunicação remota com a rede neste momento.")

def module_sistema() -> None:
    log("JARVIS", "STATUS DO SISTEMA", YELLOW)
    try:
        cpu = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory().percent
        batt_info = psutil.sensors_battery()
        batt = f"e Bateria em {int(batt_info.percent)} por cento" if batt_info else "na energia direto"
        falar_dinamico(f"Sistemas normais. Processador em {int(cpu)} por cento. Memória RAM operando com {int(ram)} por cento de uso de dados vitais. {batt}.")
    except Exception as e:
         falar_dinamico("Não foi possível acessar a placa mãe.")

def module_trabalho() -> None:
    log("JARVIS", "ABRINDO VS CODE", YELLOW)
    falar_dinamico("Preparando seu ambiente de criação chefe.")
    try: subprocess.Popen("code .", shell=True)
    except: pass

def module_clima() -> None:
    log("JARVIS", "METEOROLOGIA", YELLOW)
    try:
        loc = requests.get("https://ipinfo.io/json").json()
        lat, lon = loc['loc'].split(',')
        url_tempo = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        tempo = requests.get(url_tempo).json()['current_weather']
        falar_dinamico(f"Senhor, lá fora temos confortáveis {int(tempo['temperature'])} graus Celsius.")
    except Exception:
        falar_dinamico("Falha na varredura climática global.")

def module_trancar() -> None:
    log("JARVIS", "TRANCAR SISTEMA", RED)
    falar_dinamico("Bloqueio ativado. Protegendo perímetros focais.")
    time.sleep(1)
    os.system("rundll32.exe user32.dll,LockWorkStation")

def module_pesquisa(texto: str) -> None:
    termo = texto.split("pesquisar sobre")[-1].strip()
    log("JARVIS", f"PESQUISA: {termo}", YELLOW)
    falar_dinamico(f"Vasculhando arquivos externos sobre {termo}.")
    webbrowser.open(f"https://www.google.com/search?q={termo}")

def module_youtube() -> None:
    log("JARVIS", "ABRIR YOUTUBE", YELLOW)
    falar_dinamico("Iniciando a plataforma de vídeos.")
    webbrowser.open("https://youtube.com")

def module_whatsapp() -> None:
    log("JARVIS", "ABRIR WHATSAPP", YELLOW)
    falar_dinamico("Abrindo canal de comunicação primário.")
    webbrowser.open("https://web.whatsapp.com")

def module_github() -> None:
    log("JARVIS", "ABRIR GITHUB", YELLOW)
    falar_dinamico("Acessando repositórios do Git Hub chefe.")
    webbrowser.open("https://github.com")

def module_acordar() -> None:
    import random
    escolhido = random.choice(VOICE_ATENDIMENTO_FILES)
    log("JARVIS", "MODO ATENDIMENTO ACIONADO (Wake Word)", YELLOW)
    _play_audio_file(escolhido)


# ─────────────────────────────────────────────────────────────────────────────
# STATE MACHINE E VOSK INIT
# ─────────────────────────────────────────────────────────────────────────────

class JarvisStateMachine:
    def __init__(self):
        log("SYS", "Carregando Cérebro State-Machine...", YELLOW)
        _pre_generate_voice()
        
        self.model = vosk.Model(lang="pt")
        self.recognizer = vosk.KaldiRecognizer(self.model, SAMPLE_RATE)
        
        self.q = queue.Queue()
        self._is_running = False
        
        self.is_active = False
        self.active_time = 0.0

    def audio_callback(self, indata, frames, time_info, status):
        self.q.put(bytes(indata))

    def run_command(self, func, *args):
        self.is_active = False 
        self.recognizer = vosk.KaldiRecognizer(self.model, SAMPLE_RATE)
        threading.Thread(target=func, args=args, daemon=True).start()

    def _process_text(self, text: str):
        text = text.lower().strip()
        if not text: return

        # -----------------------------------------------------------------
        # ESTÁGIO 1: MODO PASSIVO (Só escuta a palavra "jarvis")
        # -----------------------------------------------------------------
        if not self.is_active:
             if text == "jarvis":
                 self.is_active = True
                 self.active_time = time.time()
                 log("JARVIS", "MODO ATIVADO (Ouvindo por 10s)", GREEN)
                 # Grito de Atendimento customizavel do Wake-Word
                 self.run_command(module_acordar)
             return

        # -----------------------------------------------------------------
        # ESTÁGIO 2: MODO ATIVO (Escuta comandos na janela de 10 segundos)
        # -----------------------------------------------------------------
        if time.time() - self.active_time > 10:
             log("JARVIS", "TIMEOUT. Voltando ao modo Passivo...", "\033[90m")
             self.is_active = False
             return

        log("DEBUG", f"Capturado no Estado Ativo: '{text}'", CYAN)

        if text == "jarvis liberado" or text == "liberado":
             log("JARVIS", "DESATIVADO", "\033[90m")
             self.is_active = False
             threading.Thread(target=falar_dinamico, args=("Pode deixar chefe. Descansando as válvulas.",), daemon=True).start()
             return

        # Comandos Diretos
        if text == "jarvis apresentação" or text == "apresentação":
            self.run_command(module_apresentacao)
        
        elif text == "noticias" or text == "notícias":
            self.run_command(module_noticias)
        
        elif text == "status do sistema":
            self.run_command(module_sistema)
            
        elif text == "hora do trabalho":
            self.run_command(module_trabalho)
            
        elif text == "previsao do tempo" or text == "previsão do tempo":
            self.run_command(module_clima)
            
        elif text == "trancar sistema":
            self.run_command(module_trancar)
            
        elif text.startswith("pesquisar sobre"):
            self.run_command(module_pesquisa, text)
            
        elif text == "abrir youtube":
            self.run_command(module_youtube)
            
        elif text == "abrir whatsapp":
            self.run_command(module_whatsapp)
            
        elif text == "abrir github":
            self.run_command(module_github)
            
        else:
             if len(text) > 3:
                 log("JARVIS", "COMANDO NÃO RECONHECIDO", RED)
                 self.active_time = time.time() 
                 threading.Thread(target=falar_dinamico, args=("Chefe, ordem não reconhecida. Pode mandar de novo?",), daemon=True).start()

    def start(self):
        self._is_running = True
        print(f"""
{YELLOW}
╔══════════════════════════════════════════════════════════════╗
║              J.A.R.V.I.S  SYSTEM ONLINE                      ║
║       [ARCH]: STATE MACHINE DIRECTED (Modo Ativo/Passivo)    ║
║                                                              ║
║ PARA ACORDAR      : Diga "Jarvis"                            ║
║ APÓS ACORDAR (10s): Diga o comando                           ║
║ PARA DISPENSAR    : Diga "Jarvis liberado"                   ║
║                                                              ║
║ ============ LISTA DE COMANDOS CRÍTICOS ============         ║
║ - "Jarvis apresentação" - "noticias"                         ║
║ - "status do sistema"   - "hora do trabalho"                 ║
║ - "previsao do tempo"   - "trancar sistema"                  ║
║ - "pesquisar sobre X"   - "abrir youtube"                    ║
║ - "abrir whatsapp"      - "abrir github"                     ║
╚══════════════════════════════════════════════════════════════╝
{RESET}""")
        log("MIC", "Modo Passivo Escutando. Diga 'Jarvis' para ativá-lo.", GREEN)

        try:
            with sd.RawInputStream(
                samplerate=SAMPLE_RATE, blocksize=BLOCK_SIZE, device=None,
                channels=1, dtype="int16", callback=self.audio_callback,
            ):
                while self._is_running:
                    if self.is_active and (time.time() - self.active_time > 10):
                        log("JARVIS", "TIMEOUT DE COMANDO (10s). Retornando a vigília Passiva.", "\033[90m")
                        self.is_active = False

                    if self.q.empty():
                        time.sleep(0.01)
                        continue
                        
                    data = self.q.get()
                    if self.recognizer.AcceptWaveform(data):
                        text = json.loads(self.recognizer.Result()).get("text", "")
                        if text:
                            if self.is_active: log("MIC", f"[ATIVO]: {text}", YELLOW) 
                            else: log("MIC", f"[Passivo]: {text}", "\033[90m")
                            self._process_text(text)
                            
        except KeyboardInterrupt:
            print(f"\n{YELLOW}[JARVIS] Ofuscando sistemas. Adeus.{RESET}\n")
            sys.exit(0)


if __name__ == "__main__":
    detector = JarvisStateMachine()
    detector.start()
