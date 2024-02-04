from utils.commands import AbstractCommand, CommandParsingError
from utils.logger import log


class CommandExecute(AbstractCommand):
    NAME = 'execute'
    HELP = 'Fake execute'

    def _direct(self, *args):
        if len(args) <= 1:
            raise CommandParsingError(self._current_command)
        arg_to_parse = []
        for a in reversed(args):
            if a == 'run':
                break
            arg_to_parse.append(a)
        arg_to_parse.reverse()
        print(arg_to_parse)
        self.run(*arg_to_parse)

    def run(self, *args):
        self._parse(' '.join(args))