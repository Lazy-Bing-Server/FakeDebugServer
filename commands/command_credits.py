from utils.commands import AbstractCommand
from utils.logger import log
from mcdreforged.api.rtext import *


class CommandInfo(AbstractCommand):
    NAME = 'credits'
    HELP = 'Show dummy server info'

    def _direct(self):
        log(RTextList(
            RText('--- ', RColor.gray), RText('Dummy server for MCDR'), RText(' ---', RColor.gray), '\n',
            RText('CLI Version 0.0.0 '), RText(" Work in progress", RColor.yellow)
        ))