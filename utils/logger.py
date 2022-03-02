import logging
from typing import Union
from mcdreforged.api.types import MCDReforgedLogger
from mcdreforged.api.rtext import *


LOG_FILE = 'dummy_server.log'


class DummyServerLogger(MCDReforgedLogger):
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
    FILE_FMT = MCDReforgedLogger.FILE_FMT.__class__(
        '[%(asctime)s] [%(threadName)s/%(levelname)s]: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    def __init__(self):
        super().__init__(None)

    @classmethod
    def get_console_formatter(cls, plugin_id=None):
        extra = '' if plugin_id is None else ' [{}]'.format(plugin_id)
        fmt = super().get_console_formatter().__class__
        return fmt(
            f'[%(asctime)s] [%(threadName)s/%(log_color)s%(levelname)s%(reset)s]{extra}: %(message_log_color)s%(message)s%(reset)s',
            log_colors=cls.LOG_COLORS,
            secondary_log_colors=cls.SECONDARY_LOG_COLORS,
            datefmt='%H:%M:%S'
        )

    def debug(self, *args):
        if self.VERBOSE:
            super(MCDReforgedLogger, self).debug(*args)

    def set_file(self, file_name):
        if self.file_handler is not None:
            self.removeHandler(self.file_handler)
        self.file_handler = logging.FileHandler(file_name, encoding='UTF-8')
        self.file_handler.setFormatter(self.FILE_FMT)
        self.addHandler(self.file_handler)

    @classmethod
    def get_instance(cls):
        if cls.__gl_instance is None:
            cls.__gl_instance = cls()
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
