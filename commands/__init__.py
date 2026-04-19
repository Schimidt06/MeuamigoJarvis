from .weather import WeatherCommand
from .system import (
    SystemStatsCommand, LockCommand, RestartCommand, MuteCommand,
    VolumeUpCommand, VolumeDownCommand, MinimizeCommand,
    ScreenshotCommand, ClearConsoleCommand, TimeCommand, DateCommand,
)
from .apps import (
    OpenNotepadCommand, OpenCalcCommand, OpenVSCodeCommand,
    OpenTaskMgrCommand, OpenDownloadsCommand, OpenDocumentsCommand, OpenDesktopCommand,
)
from .web import (
    SearchCommand, YouTubeCommand, GitHubCommand, WhatsAppCommand,
    WorkModeCommand, ProjectPadariaCommand, ProjectSukhafeCommand,
)
from .modes import FocusModeCommand, RelaxModeCommand

ALL_COMMANDS = [
    WeatherCommand(),
    SystemStatsCommand(), LockCommand(), RestartCommand(), MuteCommand(),
    VolumeUpCommand(), VolumeDownCommand(), MinimizeCommand(),
    ScreenshotCommand(), ClearConsoleCommand(), TimeCommand(), DateCommand(),
    OpenNotepadCommand(), OpenCalcCommand(), OpenVSCodeCommand(),
    OpenTaskMgrCommand(), OpenDownloadsCommand(), OpenDocumentsCommand(), OpenDesktopCommand(),
    SearchCommand(), YouTubeCommand(), GitHubCommand(), WhatsAppCommand(),
    WorkModeCommand(), ProjectPadariaCommand(), ProjectSukhafeCommand(),
    FocusModeCommand(), RelaxModeCommand(),
]

REGISTRY: dict = {cmd.intent: cmd for cmd in ALL_COMMANDS}
