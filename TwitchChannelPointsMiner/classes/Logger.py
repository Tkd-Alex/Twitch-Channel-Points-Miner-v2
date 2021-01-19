import logging
import emoji
import platform
import os

from pathlib import Path
from datetime import datetime


class EmojiFormatter(logging.Formatter):
    def __init__(self, *, fmt, datefmt=None, print_emoji=True):
        self.print_emoji = print_emoji
        logging.Formatter.__init__(self, fmt=fmt, datefmt=datefmt)

    def format(self, record):
        if hasattr(record, "emoji") and self.print_emoji is True:
            record.msg = emoji.emojize(
                f"{record.emoji}  {record.msg.strip()}", use_aliases=True
            )
        return super().format(record)


class LoggerSettings:
    def __init__(
        self,
        save: bool = True,
        level: int = logging.INFO,
        emoji: bool = platform.system() != "Windows",
    ):
        self.save = save
        self.level = level
        self.emoji = emoji


def configure_loggers(username, settings):
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(settings.level)
    console_handler.setFormatter(
        EmojiFormatter(
            fmt="%(asctime)s - %(levelname)s - [%(funcName)s]: %(message)s",
            datefmt="%d/%m/%y %H:%M:%S",
            print_emoji=settings.emoji,
        )
    )
    root_logger.addHandler(console_handler)

    if settings.save is True:
        logs_path = os.path.join(Path().absolute(), "logs")
        Path(logs_path).mkdir(parents=True, exist_ok=True)
        logs_file = os.path.join(
            logs_path,
            f"{username}.{datetime.now().strftime('%d%m%Y-%H%M%S')}.log",
        )
        file_handler = logging.FileHandler(logs_file, "w", "utf-8")
        file_handler.setFormatter(
            EmojiFormatter(
                fmt="%(asctime)s - %(levelname)s - %(name)s - [%(funcName)s]: %(message)s",
                datefmt="%d/%m/%y %H:%M:%S",
                print_emoji=settings.emoji,
            )
        )
        root_logger.addHandler(file_handler)
        return logs_file
    return None
