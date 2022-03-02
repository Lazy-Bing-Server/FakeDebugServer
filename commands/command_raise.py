from utils.commands import AbstractCommand


class CommandRaise(AbstractCommand):
    NAME = 'raise'
    HELP = 'Raise a command for debug'

    def _direct(self):
        raise RuntimeError('Raised on purpose')
