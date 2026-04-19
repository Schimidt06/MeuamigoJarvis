import vision
from .base import Command


class ScreenAnalysisCommand(Command):
    intent = "screen_analysis"

    def execute(self, entities, sc):
        question = entities.get("question", "O que está acontecendo nesta tela?")
        return vision.analyze_screen(question)
