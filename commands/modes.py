import webbrowser
from .base import Command


class FocusModeCommand(Command):
    intent = "mode_focus"

    def execute(self, entities, sc):
        sc.close_all_apps()
        sc.open_app("code")
        return None


class RelaxModeCommand(Command):
    intent = "mode_relax"

    def execute(self, entities, sc):
        webbrowser.open("https://www.youtube.com")
        return None
