import json
from json.decoder import JSONDecodeError
from typing import Dict, List, Union, Optional, Tuple

from mcdreforged.api.rtext import *
from mcdreforged.api.utils import Serializable, deserialize


class ClickEvent(Serializable):
    action: str
    value: str

    def get(self) -> Optional[Tuple[RAction, str]]:
        if self.action in [action.name for action in list(RAction)]:
            return RAction[self.action], self.value
        return None

    @property
    def avail(self):
        return self.get() is not None


class HoverEvent(Serializable):
    action: str
    content: Dict[str, 'RTextSerializer']

    def get(self):
        if self.action != 'show_text':
            return self.content['show_text']
        return None

    @classmethod
    def deserialize(cls, data: dict, **kwargs):
        serialized: 'HoverEvent' = deserialize(data, cls)
        if 'show_text' in serialized.content.keys():
            serialized.content['show_text'].allow_extra()

    @property
    def avail(self):
        return self.get() is not None


class RTextSerializer(Serializable):
    text: str = ''
    color: Optional[RColor] = None
    strikethrough: bool = False
    bold: bool = False
    underlined: bool = False
    obfuscated: bool = False
    italic: bool = False
    clickEvent: Optional[ClickEvent] = None
    hoverEvent: Optional[HoverEvent] = None
    extra: Optional[List['RTextSerializer']] = None
    __allow_extra: bool = False

    def get_styles(self) -> Optional[Tuple[RStyle]]:
        styles = []
        for style in list(RStyle):
            if self.__dict__[style.name]:
                styles.append(style)
        return None if len(styles) == 0 else tuple(styles)

    def allow_extra(self):
        self.__allow_extra = True

    def forbid_extra(self):
        self.__allow_extra = False

    def get(self) -> Union[RText, RTextList]:
        rt = RText(self.text, self.color, self.get_styles())
        click = self.clickEvent.get() if self.clickEvent is not None else None
        if click is not None:
            rt.c(*self.clickEvent.get())
        hover = self.hoverEvent.get() if self.hoverEvent is not None else None
        if hover is not None:
            rt.h(self.hoverEvent.get())
        if self.__allow_extra and self.extra is not None:
            return get_rtext_list(self.extra)
        return rt

    @classmethod
    def deserialize(cls, data: Union[str, dict], **kwargs):
        if isinstance(data, str):
            return data
        return deserialize(data, cls)


def get_rtext_list(original_list: list):
    rt = RTextList()
    for item in original_list:
        if isinstance(item, str):
            rt.append(item)
        elif isinstance(item, dict):
            item = RTextSerializer.deserialize(item)
            item.forbid_extra()
            rt.append(item.get())
        elif isinstance(item, list):
            rt.append(get_rtext_list(item))
    return rt


def convert_rtext(js: Union[list, dict, str]) -> RTextBase:
    if isinstance(js, str):
        try:
            js = json.loads(js)
        except JSONDecodeError:
            pass

    if isinstance(js, str):
        return RText(js)
    else:
        return RTextBase.from_json_object(js)
