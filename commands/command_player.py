from utils.commands import AbstractCommand
from utils.logger import get_logger, log
from player.online import players


class CommandPlayer(AbstractCommand):
    NAME = 'player'
    HELP = 'Manage fake player join & left'

    def _direct(self, *args):
        log("""player join <name> Fake player join
player left <name> Fake player left""")

    def join(self, name: str, ip=None):
        players.append(name, ip=ip)

    def left(self, name: str):
        players.remove(name)
