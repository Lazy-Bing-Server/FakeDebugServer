from utils.commands import AbstractCommand
from utils.logger import log


class CommandList(AbstractCommand):
    NAME = 'list'
    HELP = 'Show a fake player list'

    def _direct(self):
        log('There are 0 of a max 100 players online:')
