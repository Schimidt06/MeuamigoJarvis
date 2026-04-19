import os
import webbrowser
from .base import Command


class SearchCommand(Command):
    intent = "search"

    def execute(self, entities, sc):
        query = entities.get("query", "")
        if query:
            webbrowser.open(f"https://www.google.com/search?q={query}")
            return None
        return "Não consegui identificar o que pesquisar, senhor."


class YouTubeCommand(Command):
    intent = "youtube"

    def execute(self, entities, sc):
        webbrowser.open("https://www.youtube.com")
        return None


class GitHubCommand(Command):
    intent = "github"

    def execute(self, entities, sc):
        webbrowser.open("https://github.com")
        return None


class WhatsAppCommand(Command):
    intent = "whatsapp"

    def execute(self, entities, sc):
        webbrowser.open("https://web.whatsapp.com")
        return None


class WorkModeCommand(Command):
    intent = "work_mode"

    def execute(self, entities, sc):
        webbrowser.open(os.getenv("LANDING_PAGE_URL", "https://landing-page-schimidt.vercel.app/"))
        sc.open_app("code")
        return None


class ProjectPadariaCommand(Command):
    intent = "project_padaria"

    def execute(self, entities, sc):
        webbrowser.open("https://padaria-santo-antonio.vercel.app/")
        return None


class ProjectSukhafeCommand(Command):
    intent = "project_sukhafe"

    def execute(self, entities, sc):
        webbrowser.open("https://sukhafe.vercel.app/")
        return None
