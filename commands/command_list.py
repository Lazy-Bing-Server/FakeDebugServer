from utils.commands import AbstractCommand
from utils.logger import log
from player.online import players


class CommandList(AbstractCommand):
    NAME = 'list'
    HELP = 'Show a fake player list'

    def _direct(self, *args):
        log('There are {amount} of a max of {limit} players online:{players}'.format(
            amount=players.amount, limit=players.limit, players=' ' + ', '.join(players.player_list)))
