import os
import webbrowser
from system_control import SystemControl
from datetime import datetime
import requests
import geocoder

class CommandHandler:
    def __init__(self, voice_engine):
        self.ve = voice_engine
        self.sc = SystemControl()
        self.is_active = False
        self.last_command_time = datetime.now()

    def handle(self, text):
        text = text.lower()
        print(f"DEBUG: Handling command: {text}")

        # Basic Simple Matching for Activation - Lenient (He hears "cheguei" even if "jarvis" is clipped)
        if any(w in text for w in ["jarvis cheguei", "cheguei", "chega", "chegue", "jaime cheguei", "jarbas cheguei"]):
            self.activate()
            return

        if "liberado" in text:
            self.deactivate()
            return

        if not self.is_active:
            return

        self.last_command_time = datetime.now()
        found_command = False

        # --- COMMAND SYSTEM (Keyword-Based Matching for Flexibility) ---

        # 1. Google Search
        if "pesquisar" in text or "procure" in text:
            query = text.replace("pesquisar sobre", "").replace("pesquisar", "").replace("procure por", "").replace("procure", "").strip()
            if query:
                self.ve.falar_stark(f"Iniciando pesquisa sobre {query} nos bancos de dados globais.")
                webbrowser.open(f"https://www.google.com/search?q={query}")
                found_command = True

        # 2. YouTube
        elif "youtube" in text:
            self.ve.falar_stark("YouTube aberto, senhor.")
            webbrowser.open("https://www.youtube.com")
            found_command = True

        # 3. Weather
        elif "clima" in text or "tempo" in text:
            self.handle_weather()
            found_command = True

        # 4. Work Mode
        elif "trabalho" in text:
            self.ve.falar_stark("Ambiente de trabalho pronto, chefe. Iniciando landing page e ferramentas.")
            webbrowser.open("https://landing-page-schimidt.vercel.app/")
            self.sc.open_app("code")
            found_command = True

        # 5. System Control
        elif "status" in text and "sistema" in text:
            stats = self.sc.get_system_stats()
            self.ve.falar_stark(f"Diagnóstico concluído. CPU em {stats['cpu']}%, RAM em {stats['ram']}%, bateria em {stats['battery']}%.")
            found_command = True

        elif "trancar" in text:
            self.ve.falar_stark("Sistema bloqueado por segurança.")
            self.sc.lock_windows()
            found_command = True

        elif "reiniciar" in text:
            self.ve.falar_stark("Reiniciando sistemas em dez segundos. Até breve, senhor.")
            self.sc.restart_system()
            found_command = True

        elif "silêncio" in text or "mudo" in text:
            self.ve.falar_stark("Áudio do sistema silenciado.")
            self.sc.mute_system()
            found_command = True

        elif "volume" in text and ("aumentar" in text or "mais" in text):
            v = self.sc.change_volume(15)
            self.ve.falar_stark(f"Volume elevado para {v}%.")
            found_command = True

        elif "volume" in text and ("diminuir" in text or "menos" in text):
            v = self.sc.change_volume(-15)
            self.ve.falar_stark(f"Volume reduzido para {v}%.")
            found_command = True

        elif "minimizar" in text or "área de trabalho" in text:
            if "abrir" not in text: # Avoid confusion with opening the desktop folder
                self.ve.falar_stark("Limpando interface visual.")
                self.sc.minimize_all()
                found_command = True

        # 6. Files
        elif "downloads" in text:
            self.ve.falar_stark("Acessando pasta de transferências.")
            self.sc.open_folder("downloads")
            found_command = True

        elif "documentos" in text:
            self.ve.falar_stark("Abrindo repositório de documentos.")
            self.sc.open_folder("documentos")
            found_command = True

        elif "área de trabalho" in text and "abrir" in text:
            self.ve.falar_stark("Abrindo diretório da área de trabalho.")
            self.sc.open_folder("área de trabalho")
            found_command = True

        # 7. Apps
        elif "bloco" in text and "notas" in text:
            self.ve.falar_stark("Editor de texto básico iniciado.")
            self.sc.open_app("notepad")
            found_command = True

        elif "calculadora" in text:
            self.ve.falar_stark("Calculadora científica à disposição.")
            self.sc.open_app("calc")
            found_command = True

        elif "vscode" in text or "editor" in text:
            self.ve.falar_stark("Visual Studio Code carregando.")
            self.sc.open_app("code")
            found_command = True

        elif "gerenciador" in text or "tarefas" in text:
            self.ve.falar_stark("Exibindo gerência de processos do kernel.")
            self.sc.open_app("taskmgr")
            found_command = True

        # 8. Internet
        elif "github" in text:
            self.ve.falar_stark("Conectando ao GitHub.")
            webbrowser.open("https://github.com")
            found_command = True

        elif "whatsapp" in text:
            self.ve.falar_stark("Central de comunicações aberta.")
            webbrowser.open("https://web.whatsapp.com")
            found_command = True

        # 9. Time
        elif "horas" in text:
            now = datetime.now().strftime("%H:%M")
            self.ve.falar_stark(f"Agora são exatamente {now}, senhor.")
            found_command = True

        elif "data" in text or "hoje" in text:
            today = datetime.now().strftime("%d de %B de %Y")
            self.ve.falar_stark(f"Hoje é dia {today}.")
            found_command = True

        # 10. Smart Modes
        elif "foco" in text:
            self.ve.falar_stark("Protocolo de isolamento ativado. Eliminando distrações.")
            self.sc.close_all_apps()
            self.sc.open_app("code")
            found_command = True

        elif "relaxar" in text:
            self.ve.falar_stark("Ativando configurações de lazer. YouTube carregado.")
            webbrowser.open("https://www.youtube.com")
            found_command = True

        # 11. Gamer Mode
        elif "game" in text or "jogo" in text:
            self.ve.falar_stark("Modo jogo ativado. Otimizando processadores para renderização.")
            self.sc.close_all_apps()
            self.sc.open_app(r"C:\Users\jpsch\OneDrive\Área de Trabalho")
            found_command = True

        # 12. Utilities
        elif "print" in text or "screenshot" in text:
            f = self.sc.take_screenshot()
            self.ve.falar_stark(f"Captura de tela salva como {f}.")
            found_command = True

        elif "limpar" in text:
            os.system('cls' if os.name == 'nt' else 'clear')
            self.ve.falar_stark("Console de comando limpo.")
            found_command = True

        # Catch-all
        if not found_command:
            self.ve.falar_stark("Não entendi completamente o comando, chefe. Pode repetir?")

    def handle_weather(self):
        try:
            g = geocoder.ip('me')
            lat, lon = g.latlng
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m&daily=precipitation_probability_max&forecast_days=3&timezone=auto"
            resp = requests.get(url).json()
            
            temp = resp['current']['temperature_2m']
            rain_probs = resp['daily']['precipitation_probability_max']
            avg_rain = sum(rain_probs) / len(rain_probs)
            
            msg = f"Temperatura atual de {temp} graus. Probabilidade de chuva média de {int(avg_rain)}% nos próximos três dias."
            self.ve.falar_stark(msg)
        except:
            self.ve.falar_stark("Tive um problema ao acessar os satélites climáticos, senhor.")

    def activate(self):
        self.is_active = True
        self.last_command_time = datetime.now()
        # Responsive feedback + Cinematic Music Snippet (sec 2-6)
        self.sc.play_greeting_music()
        webbrowser.open("https://landing-page-schimidt.vercel.app/")
        webbrowser.open(f"http://localhost:{os.getenv('HUD_PORT', 5000)}")
        self.ve.falar_stark("Bem-vindo de volta, chefe. Todos os sistemas estão operacionais.")

    def deactivate(self):
        self.is_active = False
        self.ve.falar_stark("Até mais, chefe. Estarei à disposição.")
