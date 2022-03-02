from json.decoder import JSONDecodeError
import sys
import time
import threading
import traceback
import json
import re
import os

from typing import Any, Dict, List, Union, Optional, Tuple
from parse import parse
from mcdreforged.api.rtext import *
from mcdreforged.api.utils import Serializable, deserialize
from logger import *

LOG_FILE = 'dummy_server.log'
VERBOSE = True
logger = None


class DummyServerLogger(MCDReforgedLogger):
    __gl_instance = None

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
        return MCColoredFormatter(
            f'[%(asctime)s] [%(threadName)s/%(log_color)s%(levelname)s%(reset)s]{extra}: %(message_log_color)s%(message)s%(reset)s',
            log_colors=cls.LOG_COLORS,
            secondary_log_colors=cls.SECONDARY_LOG_COLORS,
            datefmt='%H:%M:%S'
        )

    def debug(self, *args):
        if VERBOSE:
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


class ClickEvent(Serializable):
    action: str
    value: str

    def get(self) -> Optional[Tuple[RAction, str]]:
        if self.action in [action.name for action in list(RAction)]:
            return RAction[self.action], self.value
        return None

    @property
    def avail(self):
        return self.get() is not None


class HoverEvent(Serializable):
    action: str
    content: Dict[str, 'RTextSerializer']

    def get(self):
        if self.action != 'show_text':
            return self.content['show_text']
        return None

    @classmethod
    def deserialize(cls, data: dict, **kwargs):
        serialized: 'HoverEvent' = deserialize(data, cls)
        if 'show_text' in serialized.content.keys():
            serialized.content['show_text'].allow_extra()

    @property
    def avail(self):
        return self.get() is not None


class RTextSerializer(Serializable):
    text: str = ''
    color: Optional[RColor] = None
    strikethrough: bool = False
    bold: bool = False
    underlined: bool = False
    obfuscated: bool = False
    italic: bool = False
    clickEvent: Optional[ClickEvent] = None
    hoverEvent: Optional[HoverEvent] = None
    extra: Optional[List['RTextSerializer']] = None
    __allow_extra: bool = False

    def get_styles(self) -> Optional[Tuple[RStyle]]:
        styles = []
        for style in list(RStyle):
            if self.__dict__[style.name]:
                styles.append(style)
        return None if len(styles) == 0 else tuple(styles)

    def allow_extra(self):
        self.__allow_extra = True

    def forbid_extra(self):
        self.__allow_extra = False

    def get(self) -> Union[RText, RTextList]:
        rt = RText(self.text, self.color, self.get_styles())
        click = self.clickEvent.get() if self.clickEvent is not None else None
        if click is not None:
            rt.c(*self.clickEvent.get())
        hover = self.hoverEvent.get() if self.hoverEvent is not None else None
        if hover is not None:
            rt.h(self.hoverEvent.get())
        if self.__allow_extra and self.extra is not None:
            return get_rtext_list(self.extra)
        return rt

    @classmethod
    def deserialize(cls, data: Union[str, dict], **kwargs):
        if isinstance(data, str):
            return data
        return deserialize(data, cls)


def get_rtext_list(original_list: list):
    rt = RTextList()
    for item in original_list:
        if isinstance(item, str):
            rt.append(item)
        elif isinstance(item, dict):
            item = RTextSerializer.deserialize(item)
            item.forbid_extra()
            rt.append(item.get())
        elif isinstance(item, list):
            rt.append(get_rtext_list(item))
    return rt


def rtext_formatter(js: Union[list, dict, str]) -> RTextBase:
    if isinstance(js, str):
        try:
            js = json.loads(js)
        except JSONDecodeError:
            pass
    if isinstance(js, list):
        return get_rtext_list(js)
    elif isinstance(js, str):
        return RText(js)
    else:
        rt = RTextSerializer.deserialize(js)
        rt = RText(rt) if isinstance(rt, str) else rt.get()
        return rt


def print_rt_struct(rt: RTextList):
    for item in rt.children:
        if isinstance(item, str):
            log(f'"{item}"')
        else:
            log(f'"{json.dumps(item.to_json_object(), indent=4)}"')


def clean_console_color_code(text):
    return re.sub(r'\033\[(\d+(;\d+)?)?m', '', text)


def print_in_format(text: Union[RTextBase, str]):
    time_text = time.strftime('[%H:%M:%S]')
    print(f'{time_text} [{threading.current_thread().getName()}/INFO]: {text}')
    with open(LOG_FILE, 'a', encoding='UTF-32') as f:
        f.write(str(f'\n{time_text} [{threading.current_thread().getName()}/INFO]: {clean_console_color_code(text)}'))


def log(msg: Union[RTextBase, str]):
    DummyServerLogger.get_instance().info(msg)


def main(start_time: float):
    running = True
    time.sleep(0.001)
    log('Starting dummy server v0.1')
    log(f'Done ({round(time.time() - start_time, 3)}s)! For help, type "help"')
    while running:
        text = input()
        try:
            if text in ['stop', 'end', 'exit']:
                log('Stopping the server')
                break
            elif text == 'list':
                log('There are 0 of a max 100 players online:')
            elif text == 'help':
                log(
                    '''stop/end/exit: Exit this dummy server
list: Show a fake player list
save/save-all: Show a fake saved message
tellraw: Show colored text''')
            elif parse('tellraw {target} {content}', text):
                psd = parse('tellraw {target} {content}', text)['content']
                try:
                    log(rtext_formatter(psd))
                except JSONDecodeError:
                    log(psd)
            elif text == 'info':
                log(RTextList(
                    RText('--- ', RColor.gray), RText('Dummy server for MCDR'), RText(' ---', RColor.gray), '\n',
                    RText('CLI Version 0.0.0 '), RText(" Work in progress", RColor.yellow)
                ))
            elif text == 'raise':
                raise RuntimeError('Raised on purpose')
            elif text.split(' ', 1)[0] in ['save', 'save-all']:
                log('Saved the game')
            else:
                log(text)
        except (EOFError, KeyboardInterrupt):
            log('Interrupted server')
            break
        except:
            log(RTextList(RText(f'Error occured in {threading.current_thread().getName()}:', RColor.red), '\n  ',
                          '\n  '.join(traceback.format_exc().splitlines())))

    log('Stopping server')


if __name__ == '__main__':
    sys.exit(main(time.time()))
