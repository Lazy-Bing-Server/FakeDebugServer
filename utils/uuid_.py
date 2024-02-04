import typing
import uuid
import hashlib
import re
import requests


def get_offline_uuid(player: str, verify_name: bool = True) -> typing.Optional[uuid.UUID]:
    if verify_name and not verify_player_name(player):
        return None
    id_ = ("OfflinePlayer:" + player).encode()
    md5 = hashlib.md5()
    md5.update(id_)
    md5_bytes = bytearray(md5.digest())
    md5_bytes[6] &= 0x0F  # clear version
    md5_bytes[6] |= 0x30  # set to version 3
    md5_bytes[8] &= 0x3F  # clear variant
    md5_bytes[8] |= 0x80  # set to IETF variant
    return uuid.UUID(bytes=bytes(md5_bytes))


def verify_player_name(player: str):
    return (re.fullmatch(r"\w+", player) is not None) and len(player) <= 16


def get_decimal(num: str):
    num = list(num)
    pos = num.pop(0) == '0'
    #pre = '' if pos else '-'
    return eval(f'0b{"".join(num)}')


def get_tuple_uuid(uuid_: uuid.UUID):
    uuid_ = [uuid_.hex[:8], uuid_.hex[8:16], uuid_.hex[16:24], uuid_.hex[24:32]]
    for item in uuid_:
        yield eval(f'(0x{item} << 1) / 0b10')


def convert_uuid_from_tuple(uuid_tuple: typing.Iterable[int]):
    uuid_tuple: typing.Tuple[int, int, int, int] = tuple(uuid_tuple)
    if len(uuid_tuple) != 4:
        raise ValueError('Invalid length iterable object input')
    ret = []
    for item in uuid_tuple:
        if item < 0:
            item = int(f'1{"0" * 8}', 16) + item
        item = format(item, 'x')
        length = 8 - len(item)
        if length > 0:
            item = length * '0' + item
        ret.append(item)
    return uuid.UUID(''.join(ret))


if __name__ == "__main__":
    target = convert_uuid_from_tuple([240899192, 1909081247, -1531449260, -1479246119])
    print(len(target.hex))
    print(target.hex)
    print(list(get_tuple_uuid(uuid_=target)))
