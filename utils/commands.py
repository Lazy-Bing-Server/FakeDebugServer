import importlib
import os
from threading import RLock, current_thread
from typing import Iterable, Union, Dict
from contextlib import contextmanager
from utils.logger import get_logger, log

from mcdreforged.api.decorator import new_thread
from mcdreforged.api.rtext import RTextBase


__all__ = [
    "AbstractCommand",
    "CommandException",
    "CommandRegistryError",
    "CommandParsingError",
]


class AbstractCommand:
    __COMMAND_EXTENSION_FOLDER = 'commands'
    SHUTDOWN_KEYWORDS = ('end', 'exit', 'stop')
    __registered: Dict[str, type] = {}
    NAME: Union[str, Iterable[str], None] = None
    cmd_gl_lock = RLock()

    def __init__(self):
        self.__cmd_cache = None

    @classmethod
    def _register(cls):
        with cls.cmd_gl_lock:
            if cls.NAME is None:
                raise CommandRegistryError(cls.NAME)
            elif isinstance(cls.NAME, str):
                if ' ' in cls.NAME.strip():
                    raise CommandRegistryError(cls.NAME)
                cls.__registered[cls.NAME.strip()] = cls
            else:
                for item in cls.NAME:
                    if ' ' in item.strip():
                        raise CommandRegistryError(cls.NAME)
                    cls.__registered[item.strip()] = cls

    @classmethod
    def _refresh(cls):
        for item in os.listdir(cls.__COMMAND_EXTENSION_FOLDER):
            if item.endswith('.py'):
                item_path = f'{cls.__COMMAND_EXTENSION_FOLDER}.{item[:-3]}'
                module = importlib.import_module(item_path)
                for name, attr in vars(module).items():
                    if not name.startswith('_') and isinstance(attr, type) and issubclass(attr, cls):
                        if attr.NAME is None:
                            continue
                        attr._register()

    @classmethod
    def _commands(cls):
        return cls.__registered

    @classmethod
    def _parse(cls, cmd: str):
        with cls.cmd_gl_lock:
            cmd = cmd.strip().split(' ')
            node = cls.__registered.get(cmd[0])
            try:
                if node is None:
                    raise CommandParsingError(' '.join(cmd))
                else:
                    node()._parse_command(*cmd)
            except CommandParsingError as e:
                cmd = e.failed_command
                if cmd is None:
                    cmd = ''
                log(cmd)


    @property
    def _methods(self):
        return {
            item: getattr(self, item) for item in list(
                filter(
                    lambda m: not m.startswith("_") and callable(getattr(self, m)),
                    dir(self)
                )
            )
        }

    @classmethod
    def _get_command_help(cls):
        msg = getattr(cls, 'HELP', '')
        prefix = cls.NAME if isinstance(cls.NAME, str) else '/'.join(cls.NAME)
        return f"{prefix}: {msg}"

    @new_thread('TaskExecutor')
    def _secure_run(self, func, *sargs, **kwargs):
        try:
            try:
                func(*sargs, **kwargs)
            except (TypeError, NotImplementedError) as e:
                raise CommandParsingError(' '.join(self.__cmd_cache))
        except Exception as exc:
            get_logger().exception(f'Exception in thread {current_thread().name}', exc_info=exc)


    @contextmanager
    def _cache_command(self, *args):
        with self.cmd_gl_lock:
            try:
                result = list(args)
                self.__cmd_cache = result.copy()
                result.pop(0)
                yield result
            finally:
                self.__cmd_cache = None

    def _parse_command(self, *args):
        with self._cache_command(*args) as editable_args:
            if len(editable_args) != 0 and editable_args[0] in self._methods.keys():
                handler = self._methods.get(editable_args.pop(0))
                self._secure_run(handler, *editable_args)
            else:
                self._secure_run(self._direct, *editable_args)

    def _direct(self, *args):
        raise NotImplementedError

    @property
    def _current_command(self):
        return self.__cmd_cache

    @classmethod
    def _get_command(cls, command: str, default=None):
        return cls.__registered.get(command, default)


class CommandException(Exception):
    pass


class CommandRegistryError(Exception):
    pass


class CommandParsingError(Exception):
    def __init__(self, command_str: str = None):
        self.__failed_command = command_str
        super(CommandParsingError, self).__init__(
            RTextBase.format('Command Error: {}', command_str)
        )

    @property
    def failed_command(self):
        return self.__failed_command
