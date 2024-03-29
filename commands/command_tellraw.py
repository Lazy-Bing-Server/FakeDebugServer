import json
from json.decoder import JSONDecodeError
from utils.commands import AbstractCommand, CommandParsingError
from utils.logger import log
from utils.raw_json_parser import convert_rtext


class CommandTellRaw(AbstractCommand):
    NAME = 'tellraw'
    HELP = 'Show colored text'
    DEBUG = False

    def _direct(self, *args):
        if len(args) <= 1:
            raise CommandParsingError(self._current_command)
        content = ' '.join(args[1:])
        try:
            log(convert_rtext(content))
            if self.DEBUG:
                log(json.dumps(json.loads(content), ensure_ascii=False, indent=4))
        except JSONDecodeError:
            log(content)
