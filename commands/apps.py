from .base import Command


class OpenNotepadCommand(Command):
    intent = "open_notepad"

    def execute(self, entities, sc):
        sc.open_app("notepad")
        return None


class OpenCalcCommand(Command):
    intent = "open_calc"

    def execute(self, entities, sc):
        sc.open_app("calc")
        return None


class OpenVSCodeCommand(Command):
    intent = "open_vscode"

    def execute(self, entities, sc):
        sc.open_app("code")
        return None


class OpenTaskMgrCommand(Command):
    intent = "open_taskmgr"

    def execute(self, entities, sc):
        sc.open_app("taskmgr")
        return None


class OpenDownloadsCommand(Command):
    intent = "open_downloads"

    def execute(self, entities, sc):
        sc.open_folder("downloads")
        return None


class OpenDocumentsCommand(Command):
    intent = "open_documents"

    def execute(self, entities, sc):
        sc.open_folder("documentos")
        return None


class OpenDesktopCommand(Command):
    intent = "open_desktop"

    def execute(self, entities, sc):
        sc.open_folder("área de trabalho")
        return None
