import sys
import threading
import time

from mcdreforged.api.decorator import new_thread
from mcdreforged.api.rtext import *

from utils.commands import AbstractCommand, CommandParsingError
from utils.logger import get_logger, log


def main(start_time: float):
    try:
        time.sleep(0.001)
        # log('Starting minecraft server version 1.19.2')
        log(f"Current encoding method: {sys.getfilesystemencoding()}")
        AbstractCommand._refresh()
        log(f'Done ({round(time.time() - start_time, 3)}s)! For help, type "help"')
        
        @new_thread('Server Thread')
        def command_exec(cmd: str):
            try:
                if len(cmd) != 0:
                    AbstractCommand._parse(cmd)
            except CommandParsingError:
                log(cmd)
            except:
                get_logger().exception(RText(f'Error occurred in {threading.current_thread().getName()}:', RColor.red))

        while True:
            text = input()
            # log(f'Parsing command {text}')
            if text in AbstractCommand.SHUTDOWN_KEYWORDS:
                log('Stopping the server')
                break
            else:
                command_exec(text)

        log('Stopping server')
    except (EOFError, KeyboardInterrupt):
        log('Server Interrupted')
    except:
        get_logger().exception(RText(f'Error occurred in {threading.current_thread().getName()}:', RColor.red))
    log('rue')


if __name__ == '__main__':
    sys.exit(main(time.time()))
