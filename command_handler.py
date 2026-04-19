import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

import brain
from commands import REGISTRY
from system_control import SystemControl
from colorama import Fore

_ACTIVATION_WORDS = {"jarvis cheguei", "cheguei", "chega", "chegue", "jaime cheguei", "jarbas cheguei"}
_DEACTIVATION_WORDS = {"liberado"}


class CommandHandler:
    def __init__(self, voice_engine, socketio=None):
        self.ve = voice_engine
        self.sc = SystemControl()
        self.socketio = socketio
        self.is_active = False
        self.last_command_time = datetime.now()
        self._executor = ThreadPoolExecutor(max_workers=2)

    def handle(self, text: str):
        text = text.lower().strip()

        if any(w in text for w in _ACTIVATION_WORDS):
            self.activate()
            return

        if any(w in text for w in _DEACTIVATION_WORDS):
            self.deactivate()
            return

        if not self.is_active:
            return

        self.last_command_time = datetime.now()
        self._executor.submit(self._process, text)

    def _process(self, text: str):
        self._emit("processing")

        result = brain.understand(text)
        intent = result.get("intent", "unknown")
        entities = result.get("entities", {})
        llm_response = result.get("response", "")

        print(f"{Fore.MAGENTA}[BRAIN]{Fore.WHITE} intent={intent} entities={entities}")

        cmd = REGISTRY.get(intent)
        if cmd:
            override = cmd.execute(entities, self.sc)
            response = override if override else llm_response
        else:
            response = llm_response

        self._emit("speaking")
        self._emit_text(response)
        self.ve.falar_stark(response)
        self._emit("listening")

    def _emit(self, state: str):
        if self.socketio:
            self.socketio.emit("state_update", {"state": state})

    def _emit_text(self, text: str):
        if self.socketio:
            self.socketio.emit("response_text", {"text": text})

    def activate(self):
        self.is_active = True
        self.last_command_time = datetime.now()
        self.ve.falar_stark("Bem-vindo de volta, chefe. Todos os sistemas estão operacionais.")
        self.sc.play_greeting_music()
        hud_port = os.getenv("HUD_PORT", 5000)
        self.sc.open_professional_window(f"http://localhost:{hud_port}")
        self._emit("listening")

    def deactivate(self):
        self.is_active = False
        self.ve.falar_stark("Até mais, chefe. Estarei à disposição.")
        self._emit("idle")
