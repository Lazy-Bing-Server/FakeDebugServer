from utils.commands import AbstractCommand
from utils.logger import log


HELP_MSG = '''stop/end/exit: Exit this dummy server
list: Show a fake player list
save/save-all: Show a fake saved message
tellraw: Show colored text'''


class CommandHelp(AbstractCommand):
    NAME = 'help'
    HELP = 'Show command help'

    def _direct(self):
        result = {f'{"/".join(self.SHUTDOWN_KEYWORDS)}: Exit this dummy server'}
        for line in self._commands().values():
            result.add(line._get_command_help())
        result = sorted(result, key=lambda a: a[0])
        log('\n'.join(result))
