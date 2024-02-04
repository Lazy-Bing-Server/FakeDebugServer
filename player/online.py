import threading

from utils.logger import get_logger
from random import uniform, randint
from ipaddress import IPv4Address


class OnlinePlayers:
    def __init__(self):
        self.__lock = threading.RLock()
        self.__id = 0
        self.__player_list = []
        self.limit = 20

    @property
    def amount(self):
        return len(self.__player_list)

    @property
    def player_list(self):
        return self.__player_list

    def is_online(self, player: str):
        return player in self.__player_list

    def append(self, name: str, ip=None) -> None:
        with self.__lock:
            if self.amount >= self.limit:
                get_logger().error('Player limit reached')
                return
            if name in self.player_list:
                get_logger().error('Player already logged in')
            else:
                self.__id += 1
                if ip is None:
                    ip = str(IPv4Address(randint(0, int(IPv4Address('255.255.255.25')))))
                port = randint(0, 65535)
                self.player_list.append(name)
                x = get_random_coordinate()
                z = get_random_coordinate()
                y = get_random_coordinate(320, 1)
                get_logger().info(f'{name}[/{ip}:{port}] logged in with entity id {self.__id} at ({x}, {y}, {z})')

    def remove(self, name: str):
        with self.__lock:
            if name not in self.player_list:
                get_logger().error('Player not found')
            else:
                self.player_list.remove(name)
                get_logger().info(f'{name} left the game')


def get_random_coordinate(limit: float = 30000000, digits=16):
    return round(uniform(- limit, limit), digits)


players = OnlinePlayers()
