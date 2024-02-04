import logging
import re
import os
import enum
from typing import Union, Optional
from mcdreforged.api.types import MCDReforgedLogger, SyncStdoutStreamHandler, Version
from mcdreforged.api.rtext import *
from colorlog import ColoredFormatter
from threading import local
from contextlib import contextmanager

LOG_FILE = 'logs/dummy_server.log'


class MCColoredFormatter(ColoredFormatter):
    if isinstance(enum.EnumMeta, RColor):
        MC_CODE_ITEMS = list(map(lambda item: item.value, list(RColor) + list(RStyle)))
    else:
        MC_CODE_ITEMS = list(
            filter(lambda item: isinstance(item, RColor) or isinstance(item, RStyle), list(RColor) + list(RStyle)))

    # global flag
    console_color_disabled = False

    __TLS = local()

    @classmethod
    @contextmanager
    def disable_minecraft_color_code_transform(cls):
        cls.__set_mc_code_trans_disable(True)
        try:
            yield
        finally:
            cls.__set_mc_code_trans_disable(False)

    @classmethod
    def __is_mc_code_trans_disabled(cls) -> bool:
        try:
            return cls.__TLS.mc_code_trans
        except AttributeError:
            cls.__set_mc_code_trans_disable(False)
            return False

    @classmethod
    def __set_mc_code_trans_disable(cls, state: bool):
        cls.__TLS.mc_code_trans = state

    def formatMessage(self, record):
        text = super().formatMessage(record)
        if not self.__is_mc_code_trans_disabled():
            # minecraft code -> console code
            for item in self.MC_CODE_ITEMS:
                if item.mc_code in text:
                    text = text.replace(item.mc_code, item.console_code)
            # clean the rest of minecraft codes
            text = clean_minecraft_color_code(text)
        if self.console_color_disabled:
            text = clean_console_color_code(text)
        return text


class NoColorFormatter(logging.Formatter):
    def formatMessage(self, record):
        return clean_console_color_code(super().formatMessage(record))


class DummyServerLogger(MCDReforgedLogger):
    logging.basicConfig(encoding='utf-8')
    __gl_instance = None

    VERBOSE = True
    SPLIT_LOG = True

    LOG_COLORS = {
        'DEBUG': 'white',
        'INFO': 'white',
        'WARNING': 'white',
        'ERROR': 'white',
        'CRITICAL': 'white',
    }

    FILE_FMT = NoColorFormatter(
            '[%(asctime)s] [%(threadName)s/%(levelname)s]: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    @classmethod
    def get_console_formatter(cls, plugin_id=None):
        extra = '' if plugin_id is None else ' [{}]'.format(plugin_id)
        formatter = MCColoredFormatter(
            f'[%(asctime)s] [%(threadName)s/%(log_color)s%(levelname)s%(reset)s]{extra}: %(message_log_color)s%(message)s%(reset)s',
            log_colors=cls.LOG_COLORS,
            secondary_log_colors=cls.SECONDARY_LOG_COLORS,
            datefmt='%H:%M:%S'
        )
        return formatter

    @property
    def __file_formatter(self):
        return self.FILE_FMT

    @property
    def __console_formatter(self):
        return self.get_console_formatter()

    def __init__(self, plugin_id=None):
        super(DummyServerLogger, self).__init__(self.DEFAULT_NAME)
        self.console_handler.setFormatter(self.__console_formatter)
        self.setLevel(logging.DEBUG)

    def debug(self, *args):
        if self.VERBOSE:
            super(MCDReforgedLogger, self).debug(*args)

    """
    def set_file(self, file_name):
        if self.file_handler is not None:
            self.removeHandler(self.file_handler)
        self.file_handler = logging.FileHandler(file_name, encoding='UTF-8')
        self.file_handler.setFormatter(self.FILE_FMT)
        self.addHandler(self.file_handler)
    """

    @classmethod
    def get_instance(cls):
        if cls.__gl_instance is None:
            cls.__gl_instance = cls()
            if not os.path.isdir(os.path.dirname(LOG_FILE)):
                os.makedirs(os.path.dirname(LOG_FILE))
            cls.__gl_instance.set_file(LOG_FILE)
        return cls.__gl_instance

    def _log(self, level: int, msg: object, *args, **kwargs) -> None:
        if isinstance(msg, RTextBase):
            msg = msg.to_colored_text()
        elif not isinstance(msg, str):
            msg = str(msg)
        if self.SPLIT_LOG:
            for line in msg.splitlines():
                super()._log(level, line, *args, **kwargs)
        else:
            super()._log(level, msg, *args, **kwargs)


def get_logger() -> DummyServerLogger:
    return DummyServerLogger.get_instance()


def log(msg: Union[RTextBase, str]):
    get_logger().info(msg)


def clean_minecraft_color_code(text):
    return re.sub('§[a-z0-9]', '', str(text))


def clean_console_color_code(text):
    return re.sub(r'\033\[(\d+(;\d+)?)?m', '', text)
