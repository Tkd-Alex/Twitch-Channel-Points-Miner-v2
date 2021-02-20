import logging
import os
import platform
from datetime import datetime
from pathlib import Path

import emoji
from colorama import Style

from TwitchChannelPointsMiner.utils import remove_emoji


class GlobalFormatter(logging.Formatter):
    def __init__(self, *, fmt, datefmt=None, print_emoji=True, print_colored=False):
        self.print_emoji = print_emoji
        self.print_colored = print_colored
        logging.Formatter.__init__(self, fmt=fmt, datefmt=datefmt)

    def format(self, record):
        record.emoji_is_present = (
            record.emoji_is_present if hasattr(record, "emoji_is_present") else False
        )
        if (
            hasattr(record, "emoji")
            and self.print_emoji is True
            and record.emoji_is_present is False
        ):
            record.msg = emoji.emojize(
                f"{record.emoji}  {record.msg.strip()}", use_aliases=True
            )
            record.emoji_is_present = True

        if self.print_emoji is False:
            if "\u2192" in record.msg:
                record.msg = record.msg.replace("\u2192", "-->")

            # With the update of Stream class It's possible that the Stream Title contains emoji
            # Full remove using a method from utils.
            record.msg = remove_emoji(record.msg)

        if self.print_colored and hasattr(record, "color"):
            record.msg = f"{record.color}{record.msg}{Style.RESET_ALL}"

        return super().format(record)


class LoggerSettings:
    def __init__(
        self,
        save: bool = True,
        less: bool = False,
        console_level: int = logging.INFO,
        file_level: int = logging.DEBUG,
        emoji: bool = platform.system() != "Windows",
        colored: bool = False,
    ):
        self.save = save
        self.less = less
        self.console_level = console_level
        self.file_level = file_level
        self.emoji = emoji
        self.colored = colored


def configure_loggers(username, settings):
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(settings.console_level)
    console_handler.setFormatter(
        GlobalFormatter(
            fmt=(
                "%(asctime)s - %(levelname)s - [%(funcName)s]: %(message)s"
                if settings.less is False
                else "%(asctime)s - %(message)s"
            ),
            datefmt=(
                "%d/%m/%y %H:%M:%S" if settings.less is False else "%d/%m %H:%M:%S"
            ),
            print_emoji=settings.emoji,
            print_colored=settings.colored,
        )
    )
    root_logger.addHandler(console_handler)

    if settings.save is True:
        logs_path = os.path.join(Path().absolute(), "logs")
        Path(logs_path).mkdir(parents=True, exist_ok=True)
        logs_file = os.path.join(
            logs_path,
            f"{username}.{datetime.now().strftime('%Y%m%d-%H%M%S')}.log",
        )
        file_handler = logging.FileHandler(logs_file, "w", "utf-8")
        file_handler.setFormatter(
            GlobalFormatter(
                fmt="%(asctime)s - %(levelname)s - %(name)s - [%(funcName)s]: %(message)s",
                datefmt="%d/%m/%y %H:%M:%S",
                print_emoji=settings.emoji,
                print_colored=settings.colored,
            )
        )
        file_handler.setLevel(settings.file_level)
        root_logger.addHandler(file_handler)
        return logs_file
    return None
