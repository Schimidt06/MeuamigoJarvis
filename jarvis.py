"""
╔══════════════════════════════════════════════════════════════╗
║                   J.A.R.V.I.S  PROTOTYPE                     ║
║            - STARK INTELLIGENCE & HQ AUDIO -                 ║
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
from bs4 import BeautifulSoup
import psutil
from dotenv import load_dotenv
import sounddevice as sd
import numpy as np
from pydub import AudioSegment
from rapidfuzz import fuzz

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
# MOTOR DE ÁUDIO HIGH-QUALITY (sounddevice + pydub)
# ─────────────────────────────────────────────────────────────────────────────

def _reproduzir_audio(segment: AudioSegment):
    """Reproduz um AudioSegment do pydub usando sounddevice sem latência."""
    try:
        # Garante que o áudio está no formato correto para o sounddevice
        samples = np.array(segment.get_array_of_samples())
        
        # Converte para float32 e normaliza
        if segment.sample_width == 2:
            samples = samples.astype(np.float32) / 32768.0
        elif segment.sample_width == 4:
            samples = samples.astype(np.float32) / 2147483648.0
            
        # Ajusta canais
        if segment.channels == 2:
            samples = samples.reshape((-1, 2))
            
        sd.play(samples, segment.frame_rate)
        sd.wait() # Aguarda o fim da reprodução
    except Exception as e:
        log("AUDIO_ERR", f"Falha na reprodução: {e}", RED)

def _gerar_e_tocar_ia(texto: str, caching=False):
    """Solicita voz à ElevenLabs, aplica melhorias e toca."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    # Settings para voz estilo Stark (mais firme/estável)
    data = {
        "text": texto,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.65, 
            "similarity_boost": 0.85,
            "style": 0.0,
            "use_speaker_boost": True
        }
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            import io
            audio_data = io.BytesIO(response.content)
            seg = AudioSegment.from_file(audio_data, format="mp3")
            
            # Aplica fade-in/out suave para evitar 'pops'
            seg = seg.fade_in(100).fade_out(100)
            _reproduzir_audio(seg)
            return True
        return False
    except: return False

def falar_stark(texto: str):
    log("JARVIS", f'"{texto[:65]}..."', MAGENTA)
    _gerar_e_tocar_ia(texto)


# ─────────────────────────────────────────────────────────────────────────────
# MÓDULOS DE COMANDO (TONY STARK TONE)
# ─────────────────────────────────────────────────────────────────────────────

def module_cheguei():
    log("JARVIS", "PROTOCOLO DE CHEGADA: ATIVADO", YELLOW)
    try: subprocess.Popen(f'start chrome --app="{URL}" --kiosk', shell=True)
    except: webbrowser.open(URL)
    
    hora = time.localtime().tm_hour
    saudacao = "Bem-vindo de volta"
    if hora < 12: saudacao = "Bom dia"
    elif hora < 18: saudacao = "Boa tarde"
    else: saudacao = "Boa noite"
    
    msg = f"{saudacao}, chefe. Os sistemas estão prontos. O mundo ainda não acabou, então acho que podemos continuar de onde paramos."
    falar_stark(msg)
    
    # Música com mixagem melhorada
    script_dir = os.path.dirname(os.path.abspath(__file__))
    music_path = os.path.join(script_dir, AUDIO_FILE)
    if os.path.isfile(music_path):
        try:
            audio = AudioSegment.from_file(music_path, format="wav")
            # Corte Stark: 2s a 6s com fade-out cinematográfico
            audio_cut = audio[2500:6500].fade_in(200).fade_out(1500)
            _reproduzir_audio(audio_cut)
        except: pass

def module_noticias():
    log("JARVIS", "VARREDURA DE SATÉLITE EM CURSO...", YELLOW)
    falar_stark("Acessando os servidores do UOL. Vou ver o que o pessoal está aprontando hoje.")
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
            texto = "Chefe, aqui está o resumo do caos: " + ". ".join(top) + ". Algo mais, ou podemos voltar ao trabalho real?"
            falar_stark(texto)
        else:
            falar_stark("Sem notícias relevantes, senhor. O que é bom, significa que ninguém quebrou nada hoje.")
    except:
        falar_dinamico("Houve uma falha na rede externa. Parece que a internet não está cooperando.")

def module_sistema():
    log("JARVIS", "DIAGNÓSTICO DE HARDWARE", YELLOW)
    try:
        cpu = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory().percent
        batt_info = psutil.sensors_battery()
        batt = f"e a bateria está em {int(batt_info.percent)} por cento" if batt_info else "e estamos ligados direto na fonte de energia"
        falar_stark(f"O processador está em {int(cpu)} por cento, o que é quase nada pra mim. A memória RAM está em {int(ram)} {batt}. Resumindo: estamos voando.")
    except:
         falar_stark("Os sensores de hardware estão um pouco instáveis agora.")

def module_clima():
    log("JARVIS", "PREVISÃO DO TEMPO", YELLOW)
    try:
        loc = requests.get("https://ipinfo.io/json").json()
        lat, lon = loc['loc'].split(',')
        url_tempo = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        tempo = requests.get(url_tempo).json()['current_weather']
        falar_stark(f"Senhor, lá fora temos {int(tempo['temperature'])} graus Celsius. Se for sair, escolha o terno certo.")
    except:
        falar_stark("Os satélites meteorológicos não estão respondendo. Talvez esteja chovendo demais onde eles estão.")

def module_trancar():
    log("JARVIS", "MODO DE DEFESA ATIVADO", RED)
    falar_stark("Entendido, senhor. Ativando protocolos de segurança. Ninguém entra, ninguém sai.")
    time.sleep(1)
    os.system("rundll32.exe user32.dll,LockWorkStation")

def module_pesquisa(texto: str):
    termo = texto.split("pesquisar sobre")[-1].strip()
    log("JARVIS", f"PESQUISA GLOBAL: {termo}", YELLOW)
    falar_stark(f"Varrendo a web por informações sobre {termo}. Vou baixar tudo pra você.")
    webbrowser.open(f"https://www.google.com/search?q={termo}")


# ─────────────────────────────────────────────────────────────────────────────
# INTELIGÊNCIA DE RECONHECIMENTO (FUZZY MATCHING)
# ─────────────────────────────────────────────────────────────────────────────

def encontrar_comando_similar(texto_ouvido: str):
    """Usa RapidFuzz para encontrar o comando mais próximo."""
    comandos = {
        "jarvis apresentação": module_cheguei,
        "apresentação": module_cheguei,
        "noticias": module_noticias,
        "notícias": module_noticias,
        "status do sistema": module_sistema,
        "hora do trabalho": lambda: falar_stark("Abrindo o VS Code. Mãos à obra.") or subprocess.Popen("code .", shell=True),
        "previsao do tempo": module_clima,
        "previsão do tempo": module_clima,
        "trancar sistema": module_trancar,
        "abrir youtube": lambda: falar_stark("Iniciando o YouTube.") or webbrowser.open("https://youtube.com"),
        "abrir whatsapp": lambda: falar_stark("WhatsApp Web na tela.") or webbrowser.open("https://web.whatsapp.com"),
        "abrir github": lambda: falar_stark("Abrindo o GitHub.") or webbrowser.open("https://github.com"),
        "jarvis liberado": "LIBERAR",
        "liberado": "LIBERAR"
    }
    
    melhor_score = 0
    melhor_comando = None
    
    for nome, func in comandos.items():
        score = fuzz.ratio(texto_ouvido, nome)
        if score > melhor_score:
            melhor_score = score
            melhor_comando = (nome, func)
            
    if melhor_score > 70:
        return melhor_comando
    return None


# ─────────────────────────────────────────────────────────────────────────────
# NÚCLEO DE ESCUTA E ESTADOS
# ─────────────────────────────────────────────────────────────────────────────

class JarvisStateMachine:
    def __init__(self):
        log("SYS", "Carregando Motores de Inteligência JARVIS...", YELLOW)
        self.model = vosk.Model(lang="pt")
        self.recognizer = vosk.KaldiRecognizer(self.model, SAMPLE_RATE)
        self.q = queue.Queue()
        self.is_active = False
        self.active_time = 0.0

    def audio_callback(self, indata, frames, time_info, status):
        self.q.put(bytes(indata))

    def _process_text(self, text: str):
        text = text.lower().strip()
        if not text: return

        # ESTÁGIO 1: WAKE WORD (Gatilho Fuzzy)
        if not self.is_active:
             score_ativacao = fuzz.ratio(text, "jarvis")
             if score_ativacao > 70 or "jarvis" in text:
                 self.is_active = True
                 self.active_time = time.time()
                 log("JARVIS", "SISTEMA ATIVADO", GREEN)
                 threading.Thread(target=falar_stark, args=("Sim, senhor. O que deseja?",), daemon=True).start()
             return

        # ESTÁGIO 2: COMANDOS
        if time.time() - self.active_time > 10:
             self.is_active = False
             return

        log("DEBUG", f"Capturado: '{text}'", CYAN)

        # Trata Pesquisa (Especial)
        if "pesquisar sobre" in text:
            self.is_active = False
            threading.Thread(target=module_pesquisa, args=(text,), daemon=True).start()
            return

        # Busca comando por similaridade
        match = encontrar_comando_similar(text)
        if match:
            nome, acao = match
            if acao == "LIBERAR":
                self.is_active = False
                threading.Thread(target=falar_stark, args=("Claro, senhor. Vou ficar na escuta.",), daemon=True).start()
            else:
                self.is_active = False
                threading.Thread(target=acao, daemon=True).start()
        else:
            if len(text) > 3:
                log("JARVIS", "COMANDO NÃO ENTENDIDO", RED)
                self.active_time = time.time() 
                falar_stark("Sinto muito, senhor. Há muito ruído ou eu simplesmente não te entendi. Pode repetir?")

    def start(self):
        print(f"\n{YELLOW}{BOLD}Assistant Online (Stark Protocol){RESET}\n")
        try:
            with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=BLOCK_SIZE, dtype="int16", channels=1, callback=self.audio_callback):
                while True:
                    if self.is_active and (time.time() - self.active_time > 10):
                        self.is_active = False
                    
                    if not self.q.empty():
                        data = self.q.get()
                        if self.recognizer.AcceptWaveform(data):
                            res = json.loads(self.recognizer.Result()).get("text", "")
                            if res: self._process_text(res)
        except KeyboardInterrupt:
            sys.exit(0)

if __name__ == "__main__":
    JarvisStateMachine().start()
