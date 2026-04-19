import os
from datetime import datetime
from .base import Command


class SystemStatsCommand(Command):
    intent = "system_stats"

    def execute(self, entities, sc):
        s = sc.get_system_stats()
        return (
            f"Diagnóstico concluído. CPU em {s['cpu']}%, "
            f"RAM em {s['ram']}%, bateria em {s['battery']}%."
        )


class LockCommand(Command):
    intent = "lock"

    def execute(self, entities, sc):
        sc.lock_windows()
        return None


class RestartCommand(Command):
    intent = "restart"

    def execute(self, entities, sc):
        sc.restart_system()
        return None


class MuteCommand(Command):
    intent = "mute"

    def execute(self, entities, sc):
        sc.mute_system()
        return None


class VolumeUpCommand(Command):
    intent = "volume_up"

    def execute(self, entities, sc):
        v = sc.change_volume(15)
        return f"Volume elevado para {v}%."


class VolumeDownCommand(Command):
    intent = "volume_down"

    def execute(self, entities, sc):
        v = sc.change_volume(-15)
        return f"Volume reduzido para {v}%."


class MinimizeCommand(Command):
    intent = "minimize"

    def execute(self, entities, sc):
        sc.minimize_all()
        return None


class ScreenshotCommand(Command):
    intent = "screenshot"

    def execute(self, entities, sc):
        f = sc.take_screenshot()
        return f"Captura de tela salva como {f}."


class ClearConsoleCommand(Command):
    intent = "clear_console"

    def execute(self, entities, sc):
        os.system("cls" if os.name == "nt" else "clear")
        return None


class TimeCommand(Command):
    intent = "time"

    def execute(self, entities, sc):
        now = datetime.now().strftime("%H:%M")
        return f"Agora são exatamente {now}, senhor."


class DateCommand(Command):
    intent = "date"

    def execute(self, entities, sc):
        today = datetime.now().strftime("%d de %B de %Y")
        return f"Hoje é {today}."
