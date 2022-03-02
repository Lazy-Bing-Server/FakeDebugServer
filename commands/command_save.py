from utils.commands import AbstractCommand
from utils.logger import log


class CommandSave(AbstractCommand):
    NAME = 'save', 'save-all'
    HELP = 'Show a fake saved message'

    def _direct(self):
        log('Saved the game')
