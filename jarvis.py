import os
import threading
import time
import webbrowser
from datetime import datetime, timedelta
from voice_engine import VoiceEngine
from command_handler import CommandHandler
from flask_server import start_server, socketio
from dotenv import load_dotenv
from colorama import init, Fore, Style

# Initialize Colorama
init(autoreset=True)

load_dotenv()

class JarvisSystem:
    def __init__(self):
        self.show_banner()
        self.ve = VoiceEngine()
        self.ch = CommandHandler(self.ve, socketio)
        self.last_active_time = datetime.now()
        self.active_timeout = int(os.getenv("ACTIVE_TIMEOUT", 600))
        self.hud_url = f"http://localhost:{os.getenv('HUD_PORT', 5000)}"
        self.is_running = True

    def show_banner(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        banner = f"""
{Fore.CYAN}{Style.BRIGHT}    
    ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗
    ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝
    ██║███████║██████╔╝██║   ██║██║███████╗
    ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║
    ██║██║  ██║██║  ██║ ╚████╔╝ ██║███████║
    ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝
{Fore.BLUE}    -------------------------------------------
{Fore.WHITE}    MARC VII - LOCAL ASSISTANT SYSTEM
{Fore.BLUE}    -------------------------------------------
        """
        print(banner)
        print(f"{Fore.GREEN}[SYSTEM]{Fore.WHITE} Iniciando protocolos de segurança...")
        print(f"{Fore.GREEN}[SYSTEM]{Fore.WHITE} Carregando HUD e Banco de Dados...")

    def monitor_timeout(self):
        while self.is_running:
            if self.ch.is_active:
                if datetime.now() > self.ch.last_command_time + timedelta(seconds=self.active_timeout):
                    print(f"\n{Fore.YELLOW}[TIMEOUT]{Fore.WHITE} Modo ativo encerrado por inatividade.")
                    self.ch.is_active = False
            time.sleep(1)

    def on_voice_command(self, text):
        # Colorful logging for commands
        status = f"{Fore.CYAN}[AUTO]{Fore.WHITE}" if self.ch.is_active else f"{Fore.YELLOW}[PASS]{Fore.WHITE}"
        print(f"{status} Captação: {Fore.WHITE}{text}")
        
        self.ch.handle(text)
        
        if self.ch.is_active and not hasattr(self, '_hud_opened'):
            self.open_hud()
            self._hud_opened = True
        
        if not self.ch.is_active and hasattr(self, '_hud_opened'):
            delattr(self, '_hud_opened')

    def open_hud(self):
        print(f"{Fore.GREEN}[HUD]{Fore.WHITE} Interface visual aberta no navegador.")
        try:
            webbrowser.open(self.hud_url)
        except Exception as e:
            print(f"{Fore.RED}[ERR]{Fore.WHITE} Erro ao abrir HUD: {e}")

    def start(self):
        # 1. Start Flask
        flask_thread = threading.Thread(target=start_server, daemon=True)
        flask_thread.start()
        print(f"{Fore.GREEN}[SRV]{Fore.WHITE} Servidor HUD iniciado na porta {os.getenv('HUD_PORT', 5000)}")

        # 2. Start Timeout Monitor
        timeout_thread = threading.Thread(target=self.monitor_timeout, daemon=True)
        timeout_thread.start()

        # 3. JARVIS starts silently
        print(f"\n{Fore.CYAN}{Style.BRIGHT}JARVIS{Fore.WHITE} está ouvindo... (Modo Passivo)")
        try:
            self.ve.listen(self.on_voice_command)
        except KeyboardInterrupt:
            self.is_running = False
            print(f"\n{Fore.RED}[OFF]{Fore.WHITE} Desligando sistemas... Até logo, senhor.")

if __name__ == "__main__":
    jarvis = JarvisSystem()
    jarvis.start()
