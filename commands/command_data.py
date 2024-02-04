from utils.commands import AbstractCommand, CommandParsingError
from utils.logger import log
from typing import Optional, Union, List, Dict, Any
import json
import collections

from player.online import players


_NOT_FOUND = object()
Coordinate = collections.namedtuple('Coordinate', 'x y z')


class CommandData(AbstractCommand):
    FAKE_BLOCK_TITLE = '{x}, {y}, {z} has the following block data: '
    FAKE_BLOCK_RAW = '{z: %ZVALUE%, powered: 0b, x: %XVALUE%, auto: 0b, UpdateLastExecution: 1b, id: "minecraft:command_block", y: %YVALUE%, conditionMet: 0b, Command: "", SuccessCount: 0, CustomName: \'{"text":"@"}\', TrackOutput: 1b}'
    FAKE_BLOCK_DATA = {
        "z": -19,
        "powered": 0,
        "x": 565,
        "auto": 0,
        "UpdateLastExecution": 1,
        "id": "minecraft:command_block",
        "y": 100,
        "conditionMet": 0,
        "Command": "",
        "SuccessCount": 0,
        "CustomName": "{\"text\":\"@\"}",
        "TrackOutput": 1
    }

    FAKE_PLAYER_TITLE = "{player} has the following entity data: "
    FAKE_PLAYER_RAW = '{seenCredits: 0b, DeathTime: 0s, foodTickTimer: 0, recipeBook: {isBlastingFurnaceFilteringCraftable: 0b, isGuiOpen: 0b, toBeDisplayed: [], isFurnaceFilteringCraftable: 0b, isBlastingFurnaceGuiOpen: 0b, isFurnaceGuiOpen: 0b, isSmokerGuiOpen: 0b, isFilteringCraftable: 0b, isSmokerFilteringCraftable: 0b, recipes: []}, OnGround: 1b, AbsorptionAmount: 0.0f, XpTotal: 0, playerGameType: 1, Attributes: [{Name: "minecraft:generic.movement_speed", Base: 0.10000000149011612d}], Invulnerable: 0b, SelectedItemSlot: 0, Brain: {memories: {}}, Dimension: "minecraft:overworld", abilities: {walkSpeed: 0.1f, flySpeed: 0.05f, instabuild: 1b, flying: 0b, mayfly: 1b, invulnerable: 1b, mayBuild: 1b}, Score: 0, Rotation: [0.0f, 0.0f], HurtByTimestamp: 0, foodSaturationLevel: 5.0f, Air: 300s, EnderItems: [], XpSeed: 1266479716, foodLevel: 20, UUID: [I; 240899192, 1909081247, -1531449260, -1479246119], XpLevel: 0, Inventory: [], Motion: [0.0d, -0.0784000015258789d, 0.0d], FallDistance: 0.0f, DataVersion: 2586, SleepTimer: 0s, XpP: 0.0f, previousPlayerGameType: -1, Health: 20.0f, HurtTime: 0s, Pos: [174.0d, 1.0d, -184.0d], FallFlying: 0b, Fire: -20s, PortalCooldown: 0, foodExhaustionLevel: 0.0f}'
    FAKE_PLAYER_DATA = {
        "seenCredits": 0,
        "DeathTime": 0,
        "foodTickTimer": 0,
        "recipeBook": {
            "isBlastingFurnaceFilteringCraftable": 0,
            "isGuiOpen": 0,
            "toBeDisplayed": [],
            "isFurnaceFilteringCraftable": 0,
            "isBlastingFurnaceGuiOpen": 0,
            "isFurnaceGuiOpen": 0,
            "isSmokerGuiOpen": 0,
            "isFilteringCraftable": 0,
            "isSmokerFilteringCraftable": 0,
            "recipes": []
        },
        "OnGround": 1,
        "AbsorptionAmount": 0,
        "XpTotal": 0,
        "playerGameType": 1,
        "Attributes": [
            {
                "Name": "minecraft:generic.movement_speed",
                "Base": 0.10000000149011612
            }
        ],
        "Invulnerable": 0,
        "SelectedItemSlot": 0,
        "Brain": {
            "memories": {}
        },
        "Dimension": "minecraft:overworld",
        "abilities": {
            "walkSpeed": 0.1,
            "flySpeed": 0.05,
            "instabuild": 1,
            "flying": 0,
            "mayfly": 1,
            "invulnerable": 1,
            "mayBuild": 1
        },
        "Score": 0,
        "Rotation": [
            0,
            0
        ],
        "HurtByTimestamp": 0,
        "foodSaturationLevel": 5,
        "Air": 300,
        "EnderItems": [],
        "XpSeed": 1266479716,
        "foodLevel": 20,
        "UUID": [
            240899192,
            1909081247,
            -1531449260,
            -1479246119
        ],
        "XpLevel": 0,
        "Inventory": [],
        "Motion": [
            0,
            -0.0784000015258789,
            0
        ],
        "FallDistance": 0,
        "DataVersion": 2586,
        "SleepTimer": 0,
        "XpP": 0,
        "previousPlayerGameType": -1,
        "Health": 20,
        "HurtTime": 0,
        "Pos": [
            174,
            1,
            -184
        ],
        "FallFlying": 0,
        "Fire": -20,
        "PortalCooldown": 0,
        "foodExhaustionLevel": 0
    }

    FAKE_STORAGE_DATA = "Storage {storage} has the following contents: {}"
    FAKE_STORAGE = "{}"

    NAME = 'data'
    HELP = 'Show a fake data'

    @staticmethod
    def __is_float(string: str):
        try:
            float(string)
            return True
        except ValueError:
            return False

    def _full_cmd(self, *args):
        return f'{self.NAME} {" ".join(*args)}'

    def __display_player_message(self, player: str, path: Optional[str] = None):
        title = self.FAKE_PLAYER_TITLE.format(player=player)
        data = self.__get_dict_item(self.FAKE_PLAYER_DATA, list(path.split('.')))
        if path is None:
            log(title + self.FAKE_PLAYER_RAW)
        elif data is _NOT_FOUND:
            log(f'Found no elements matching {path}')
        else:
            log(title + data)

    def __display_block_message(self, pos: Coordinate, path: Optional[str] = None):
        title = self.FAKE_BLOCK_TITLE.format(x=pos.x, y=pos.y, z=pos.z)
        data = self.FAKE_BLOCK_DATA
        data['x'], data['y'], data['z'] = pos.x, pos.y, pos.z
        data = self.__get_dict_item(self.FAKE_BLOCK_DATA, list(path.split('.')))
        if path is None:
            log(title + self.FAKE_BLOCK_RAW.replace('%ZVALUE%', str(pos.z)).replace('%YVALUE%', str(pos.y)).replace('%XVALUE%', str(pos.x)))
        elif data is _NOT_FOUND:
            log(f'Found no elements matching {path}')
        else:
            log(title + data)

    @staticmethod
    def __get_dict_item(data: Dict[str, Any], path: List[str], fallback: Any = _NOT_FOUND):
        path = path.copy()
        data: Union[dict, Any]
        if len(path) == 0:
            return fallback
        while True:
            key = path.pop(0)
            if not isinstance(data, dict) or key not in data.keys():
                return fallback
            data = data[key]
            if len(path) == 0:
                break
        if not isinstance(data, (str, int, float)):
            data = json.dumps(data, ensure_ascii=False)
        return data

    def get(self, target: str, *args: str):
        arg_list = list(args)
        if target == 'entity':
            if len(arg_list) in [1, 2]:
                path = None
                player = arg_list[0]
                if not players.is_online(player):
                    log('No entity was found')
                    return
                if len(arg_list) == 2:
                    path = arg_list[1]
                self.__display_player_message(player, path=path)
            else:
                raise CommandParsingError(self._full_cmd(target, *args))

        elif target == 'block':
            if len(arg_list) not in [3, 4] or any([isinstance(p, (int, float)) for p in arg_list[:3]]):
                raise CommandParsingError(self._full_cmd(target, *args))
            pos = Coordinate(*arg_list[:3])
            path = None
            if len(arg_list) == 4:
                path = arg_list[3]
            self.__display_block_message(pos, path)

        else:
            if len(arg_list) not in [1, 2]:
                raise CommandParsingError(self._full_cmd(target, *args))
            storage_name = arg_list[0].strip()
            namespace = storage_name.split(':', maxsplit=1)
            if namespace == storage_name:
                storage_name = f'minecraft:{storage_name}'
            log(f"Storage {storage_name} has the following contents: {self.FAKE_STORAGE}")
