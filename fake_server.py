from json.decoder import JSONDecodeError
import sys
import time
import threading
import traceback
import json
import re
import os

from typing import Any, Dict, List, Union
from parse import parse
from mcdreforged.api.rtext import *
from mcdreforged.api.types import MCDReforgedLogger


LOG_FILE = 'dummy_server.log'


def rtext_formatter(js, ignore_hover=False) -> RTextBase:
    if isinstance(js, Dict):
        if js.get('text') is not None:
            rt = RText(js['text'])
        elif js.get('translate') is not None:
            rt = RTextTranslation(js['translate'])
        color = js.get('color')
        if color is not None:
            rt.set_color(RColor[color])
        for st in RStyle:
            if js.get(st.name):
                rt.set_styles(st)
        ce = js.get('clickEvent')
        if ce is not None:
            rt.c(RAction[ce['action']], ce['value'])
        he = js.get('hoverEvent')
        if he is not None and not ignore_hover:
            rt.h(rtlist_formatter(he['extra']))
        return rt
    if isinstance(js, List):
        return rtlist_formatter(js)
    raise TypeError("This type can't be formatted into RText")


def rtlist_formatter(js: List[dict], ignore_hover=False) -> RTextList:
    if not isinstance(js, List):
        raise TypeError('RTextlist can only be converted from list')
    rt = RTextList()
    for item in js:
        if isinstance(item, str):
            rt.append(item)
        else:
            rt.append(rtext_formatter(item, ignore_hover))
    rt.set_color(None)
    return rt


def clean_console_color_code(text):
	return re.sub(r'\033\[(\d+(;\d+)?)?m', '', text)


def log(msg: Union[RTextBase, str]):
    if isinstance(msg, RTextBase):
        msg = msg.to_colored_text()
    time_text = time.strftime('[%H:%M:%S]')
    for m in msg.splitlines():
        print(f'{time_text} [{threading.current_thread().getName()}/INFO]: {m}')
        with open(LOG_FILE, 'a', encoding='UTF-8') as f:
            f.write(f'\n{time_text} [{threading.current_thread().getName()}/INFO]: {clean_console_color_code(m)}')


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
                    log(rtext_formatter(json.loads(psd)))
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
        except Exception as e:
            log(RTextList(RText(f'Error occured in {threading.current_thread().getName()}:', RColor.red), '\n  ', '\n  '.join(traceback.format_exc().splitlines())))

    log('Stopping server')


if __name__ == '__main__':
    sys.exit(main(time.time()))
