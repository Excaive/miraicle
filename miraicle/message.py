import time
import random
import base64 as b64
from typing import Optional, Union, List
from abc import ABC, abstractmethod

from .utils import color


class Element(ABC):
    """消息元素基类"""

    @abstractmethod
    def to_json(self):
        """将消息对象转换为 json"""

    @staticmethod
    @abstractmethod
    def from_json(json: dict):
        """将 json 转换为消息对象"""

    @classmethod
    def subclasses_str(cls):
        """返回所有子类名字符串的列表"""
        return [c.__name__ for c in cls.__subclasses__()]

    @classmethod
    def _handle_base64(cls, base64: Optional[Union[bytes, str]]) -> Optional[bytes]:
        if isinstance(base64, str):
            return b64.b64encode(open(base64, 'rb').read())
        else:
            return base64


class Plain(Element):
    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return self.text

    def __eq__(self, other):
        if isinstance(other, Plain):
            return self.text == other.text
        else:
            return False

    def to_json(self):
        return {'type': 'Plain', 'text': self.text}

    @staticmethod
    def from_json(json: dict):
        text = json.get('text', None)
        return Plain(text)


class At(Element):
    def __init__(self, qq, display: str = None):
        self.qq = qq
        self.display = display

    def __repr__(self):
        if self.display:
            return f'[At:{self.qq} | {self.display}]'
        else:
            return f'[At:{self.qq}]'

    def __eq__(self, other):
        if isinstance(other, At):
            return self.qq == other.qq
        else:
            return False

    def to_json(self):
        return {'type': 'At', 'target': self.qq}

    @staticmethod
    def from_json(json: dict):
        qq = json.get('target', None)
        display = json.get('display', None)
        return At(qq, display)


class AtAll(Element):
    def __init__(self):
        pass

    def __repr__(self):
        return '[AtAll]'

    def __eq__(self, other):
        if isinstance(other, AtAll):
            return True
        else:
            return False

    def to_json(self):
        return {'type': 'AtAll'}

    @staticmethod
    def from_json(json: dict):
        return AtAll()


class Face(Element):
    def __init__(self, face_id: int = None, name: str = None):
        self.face_id = face_id
        self.name = name

    def __repr__(self):
        if self.face_id and self.name:
            return f'[Face:{self.face_id} | {self.name}]'
        elif self.face_id:
            return f'[Face:{self.face_id}]'
        else:
            return f'[Face:{self.name}]'

    def __eq__(self, other):
        if isinstance(other, Face):
            return self.face_id == other.face_id if self.face_id and other.face_id else self.name == other.name
        else:
            return False

    def to_json(self):
        if self.face_id:
            return {'type': 'Face', 'faceId': self.face_id}
        else:
            return {'type': 'Face', 'name': self.name}

    @staticmethod
    def from_json(json: dict):
        face_id = json.get('faceId', None)
        name = json.get('name', None)
        return Face(face_id, name)

    @staticmethod
    def from_face_id(face_id: int):
        return Face(face_id=face_id)

    @staticmethod
    def from_name(name: str):
        return Face(name=name)


class Image(Element):
    def __init__(self, path: str = None, url: str = None, image_id: str = None,
                 base64: Optional[Union[bytes, str]] = None):
        self.path = path
        self.url = url
        self.image_id = image_id
        self.base64 = Element._handle_base64(base64)

    def __repr__(self):
        if not self.image_id:
            return '[Image]'
        elif not self.url:
            return f'[Image:{self.image_id}]'
        else:
            return f'[Image:{self.image_id} | {self.url}]'

    def __eq__(self, other):
        if isinstance(other, Image):
            return self.image_id == other.image_id
        else:
            return False

    def to_json(self):
        if self.path:
            return {'type': 'Image', 'path': self.path}
        elif self.url:
            return {'type': 'Image', 'url': self.url}
        elif self.image_id:
            return {'type': 'Image', 'imageId': self.image_id}
        elif self.base64:
            return {'type': 'Image', 'base64': self.base64.decode('utf-8')}

    @property
    def is_flash(self) -> bool:
        return False

    def to_flash(self) -> 'FlashImage':
        return FlashImage(path=self.path, url=self.url, image_id=self.image_id)

    def to_normal(self) -> 'Image':
        return self

    @staticmethod
    def from_json(json: dict) -> 'Image':
        path = json.get('path', None)
        url = json.get('url', None)
        image_id = json.get('imageId', None)
        return Image(path, url, image_id)

    @staticmethod
    def from_file(path: str) -> 'Image':
        return Image(path=path)

    @staticmethod
    def from_url(url: str) -> 'Image':
        return Image(url=url)

    @staticmethod
    def from_id(image_id: str) -> 'Image':
        return Image(image_id=image_id)

    @staticmethod
    def from_base64(base64) -> 'Image':
        return Image(base64=Element._handle_base64(base64))


class FlashImage(Element):
    def __init__(self, path: str = None, url: str = None, image_id: str = None,
                 base64: Optional[Union[bytes, str]] = None):
        self.path = path
        self.url = url
        self.image_id = image_id
        self.base64 = Element._handle_base64(base64)

    def __repr__(self):
        if not self.image_id:
            return '[FlashImage]'
        elif not self.url:
            return f'[FlashImage:{self.image_id}]'
        else:
            return f'[FlashImage:{self.image_id} | {self.url}]'

    def __eq__(self, other):
        if isinstance(other, FlashImage):
            return self.image_id == other.image_id
        else:
            return False

    def to_json(self):
        if self.path:
            return {'type': 'FlashImage', 'path': self.path}
        elif self.url:
            return {'type': 'FlashImage', 'url': self.url}
        elif self.image_id:
            return {'type': 'FlashImage', 'imageId': self.image_id}
        elif self.base64:
            return {'type': 'FlashImage', 'base64': self.base64.decode('utf-8')}

    @property
    def is_flash(self) -> bool:
        return True

    def to_normal(self) -> Image:
        return Image(path=self.path, url=self.url, image_id=self.image_id)

    def to_flash(self) -> 'FlashImage':
        return self

    @staticmethod
    def from_json(json: dict) -> 'FlashImage':
        path = json.get('path', None)
        url = json.get('url', None)
        image_id = json.get('imageId', None)
        return FlashImage(path, url, image_id)

    @staticmethod
    def from_file(path: str) -> 'FlashImage':
        return FlashImage(path=path)

    @staticmethod
    def from_url(url: str) -> 'FlashImage':
        return FlashImage(url=url)

    @staticmethod
    def from_id(image_id: str) -> 'FlashImage':
        return FlashImage(image_id=image_id)

    @staticmethod
    def from_base64(base64) -> 'FlashImage':
        return FlashImage(base64=Element._handle_base64(base64))


class Voice(Element):
    def __init__(self, path: str = None, url: str = None, voice_id: str = None,
                 base64: Optional[Union[bytes, str]] = None, length: int = 0):
        self.path = path
        self.url = url
        self.voice_id = voice_id
        self.base64 = Element._handle_base64(base64)
        self.length = length

    def __repr__(self):
        if not self.voice_id:
            return '[Voice]'
        elif not self.url:
            return f'[Voice:{self.voice_id}]'
        else:
            return f'[Voice:{self.voice_id} | {self.url}]'

    def __eq__(self, other):
        if isinstance(other, Voice):
            return self.voice_id == other.voice_id
        else:
            return False

    def to_json(self):
        if self.path:
            return {'type': 'Voice', 'path': self.path}
        elif self.url:
            return {'type': 'Voice', 'url': self.url}
        elif self.voice_id:
            return {'type': 'Voice', 'voiceId': self.voice_id}
        elif self.base64:
            return {'type': 'Voice', 'base64': self.base64.decode('utf-8')}

    @staticmethod
    def from_json(json: dict) -> 'Voice':
        path = json.get('path', None)
        url = json.get('url', None)
        voice_id = json.get('voiceId', None)
        length = json.get('length', 0)
        return Voice(path, url, voice_id, length=length)

    @staticmethod
    def from_file(path: str) -> 'Voice':
        return Voice(path=path)

    @staticmethod
    def from_url(url: str) -> 'Voice':
        return Voice(url=url)

    @staticmethod
    def from_id(voice_id: str) -> 'Voice':
        return Voice(voice_id=voice_id)

    @staticmethod
    def from_base64(base64) -> 'Voice':
        return Voice(base64=Element._handle_base64(base64))


class Xml(Element):
    def __init__(self, xml):
        self.xml = xml

    def __repr__(self):
        return f'[Xml:{self.xml}]'

    def __eq__(self, other):
        if isinstance(other, Xml):
            return self.xml == other.xml
        else:
            return False

    def to_json(self):
        return {'type': 'Xml', 'xml': self.xml}

    @staticmethod
    def from_json(json: dict):
        xml = json.get('xml', None)
        return Xml(xml=xml)


class Json(Element):
    def __init__(self, json):
        self.json = json

    def __repr__(self):
        return f'[Json:{self.json}]'

    def __eq__(self, other):
        if isinstance(other, Json):
            return self.json == other.json
        else:
            return False

    def to_json(self):
        return {'type': 'Json', 'json': self.json}

    @staticmethod
    def from_json(json: dict):
        json = json.get('json', None)
        return Json(json=json)


class App(Element):
    def __init__(self, content):
        self.content = content

    def __repr__(self):
        return f'[App:{self.content}]'

    def __eq__(self, other):
        if isinstance(other, App):
            return self.content == other.content
        else:
            return False

    def to_json(self):
        return {'type': 'App', 'content': self.content}

    @staticmethod
    def from_json(json: dict):
        json = json.get('content', None)
        return App(content=json)


class Poke(Element):
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f'[Poke:{self.name}]'

    def __eq__(self, other):
        if isinstance(other, Poke):
            return self.name == other.name
        else:
            return False

    def to_json(self):
        return {'type': 'Poke', 'name': self.name}

    @staticmethod
    def from_json(json: dict):
        name = json.get('name', None)
        return Poke(name=name)


class Dice(Element):
    def __init__(self, value: Optional[int] = None):
        self.value = value if value else random.randint(1, 6)

    def __repr__(self):
        return f'[Dice:{self.value}]'

    def __eq__(self, other):
        if isinstance(other, Dice):
            return self.value == other.value
        else:
            return False

    def to_json(self):
        return {'type': 'Dice', 'value': self.value}

    @staticmethod
    def from_json(json: dict):
        value = json.get('value', None)
        return Dice(value=value)


class File(Element):
    def __init__(self, file_id: str, name: str, size: int):
        self.file_id = file_id
        self.name = name
        self.size = size

    def __repr__(self):
        return f'[File:{self.name} | {self.file_id}]'

    def __eq__(self, other):
        if isinstance(other, File):
            return self.file_id == other.file_id and self.name == other.name and self.size == other.size
        else:
            return False

    def to_json(self):
        return {'type': 'File', 'id': self.file_id, 'name': self.name, 'size': self.size}

    @staticmethod
    def from_json(json: dict):
        file_id = json.get('id', None)
        name = json.get('name', None)
        size = json.get('size', None)
        return File(file_id=file_id, name=name, size=size)


class MiraiCode(Element):
    def __init__(self, code: str):
        self.code = code

    def __repr__(self):
        return f'[MiraiCode:{self.code}]'

    def __eq__(self, other):
        if isinstance(other, MiraiCode):
            return self.code == other.code
        else:
            return False

    def to_json(self):
        return {'type': 'MiraiCode', 'code': self.code}

    @staticmethod
    def from_json(json: dict):
        code = json.get('code', None)
        return MiraiCode(code=code)


class BotMessage:
    """bot 发出的消息"""

    def __init__(self, msg_chain: List, msg_type: str = None, msg_id: int = None, target: int = None):
        self.chain = msg_chain
        self.msg_type = msg_type
        self.id = msg_id
        self.text = ''
        self.target = target
        for ele in self.chain:
            if ele['type'] in Element.subclasses_str():
                self.text += eval(ele['type']).from_json(ele).__repr__()

    def __repr__(self):
        return f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} {self.msg_type} #{self.id} - " \
               f"{self.target} <- {self.text.__repr__()}"


class Message:
    """消息基类"""

    def __init__(self, msg: dict, bot_qq: int):
        self.json = msg
        self._bot_qq = bot_qq
        msg_chain = msg.get('messageChain', None)
        try:
            self.id = msg_chain[0].get('id', None)
        except:
            self.id = None
        self.time = msg_chain[0].get('time', 0)
        try:
            self._time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.time))
        except:
            self._time = None

        try:
            chain = []
            text = ''
            for ele in msg_chain[1:]:
                if ele['type'] in Element.subclasses_str():
                    instance = eval(ele['type']).from_json(ele)
                    chain.append(instance)
                    text += instance.__repr__()
                else:
                    text += f"[{ele['type']}]"
            self.chain = chain
            self.text = text
        except:
            self.chain = []
            self.text = ''

    def __eq__(self, other):
        if isinstance(other, Message):
            return True if self.chain == other.chain else False
        return False

    @property
    def plain(self) -> str:
        """返回消息链中的所有文字"""
        text = ''
        for ele in self.chain:
            if type(ele) == Plain:
                text += ele.text
        return text

    @property
    def first_image(self) -> Optional[Union[Image, FlashImage]]:
        """返回消息链中的第一张图片"""
        for ele in self.chain:
            if isinstance(ele, (Image, FlashImage)):
                return ele
        return None

    @property
    def images(self) -> List[Union[Image, FlashImage]]:
        """返回消息链中所有图片的列表"""
        return [ele for ele in self.chain if isinstance(ele, (Image, FlashImage))]

    @property
    def voice(self) -> Optional[Voice]:
        """返回消息链中的语音"""
        for ele in self.chain:
            if isinstance(ele, Voice):
                return ele
        return None

    @property
    def file(self) -> Optional[File]:
        """返回消息链中的文件"""
        for ele in self.chain:
            if isinstance(ele, File):
                return ele
        return None

    def at_me(self) -> bool:
        """返回这条消息中是否 at 了 bot"""
        return any([ele == At(self._bot_qq) for ele in self.chain])


class GroupMessage(Message):
    """群消息"""

    def __init__(self, msg: dict, bot_qq: int):
        super().__init__(msg, bot_qq)
        sender = msg.get('sender', {})
        self.sender = sender.get('id', None)
        self.sender_name = sender.get('memberName', None)
        group = sender.get('group', {})
        self.group = group.get('id', None)
        self.group_name = group.get('name', None)

    def __repr__(self):
        return f'{self._time} GroupMessage #{self.id} {self.group_name}({self.group})' \
               f' - {self.sender_name}({self.sender}): {self.text.__repr__()}'


class FriendMessage(Message):
    """好友消息"""

    def __init__(self, msg: dict, bot_qq: int):
        super().__init__(msg, bot_qq)
        sender = msg.get('sender', {})
        self.sender = sender.get('id', None)
        self.sender_name = sender.get('nickname', None)

    def __repr__(self):
        return f'{self._time} FriendMessage #{self.id}' \
               f' - {self.sender_name}({self.sender}): {self.text.__repr__()}'


class TempMessage(Message):
    """群临时消息"""

    def __init__(self, msg: dict, bot_qq: int):
        super().__init__(msg, bot_qq)
        sender = msg.get('sender', {})
        self.sender = sender.get('id', None)
        self.sender_name = sender.get('memberName', None)
        group = sender.get('group', {})
        self.group = group.get('id', None)
        self.group_name = group.get('name', None)

    def __repr__(self):
        return f'{self._time} TempMessage #{self.id} {self.group_name}({self.group})' \
               f' - {self.sender_name}({self.sender}): {self.text.__repr__()}'


class GroupRecallEvent:
    def __init__(self, msg: dict):
        self.json = msg
        self.id = msg.get('messageId', None)
        self.author = msg.get('authorId', None)
        group = msg.get('group', {})
        self.group = group.get('id', None)
        self.group_name = group.get('name', None)
        operator = msg.get('operator', {})
        self.operator = operator.get('id', None)
        self.operator_name = operator.get('memberName', None)
        self.operator_permission = operator.get('permission', None)

    def __repr__(self):
        return f'GroupRecallEvent #{self.id} {self.group_name}({self.group})' \
               f' - {self.operator_name}({self.operator}) recalled a message from {self.author}'


class MemberCardChangeEvent:
    def __init__(self, msg: dict):
        self.json = msg
        self.origin = msg.get('origin', None)
        self.current = msg.get('current', None)
        member = msg.get('member', {})
        self.member = member.get('id', None)
        self.member_name = member.get('memberName', None)
        group = member.get('group', {})
        self.group = group.get('id', None)
        self.group_name = group.get('name', None)
        operator = msg.get('operator', {})
        if operator is None:
            operator = {}
        self.operator = operator.get('id')
        self.operator_name = operator.get('memberName', None)
        self.operator_permission = operator.get('permission', None)

    def __repr__(self):
        return f"MemberCardChangeEvent {self.group_name}({self.group})" \
               f" - {self.member_name}({self.member})'s card was changed from '{self.origin}' to '{self.current}'" \
               f" by {self.operator_name}({self.operator})"


class BotOnlineEvent:
    def __init__(self, msg: dict):
        self.json = msg
        self.type = msg.get('type', None)

    def __repr__(self):
        return color(self.type, 'green')


class BotOfflineEvent:
    def __init__(self, msg: dict):
        self.json = msg
        self.type = msg.get('type', None)

    def __repr__(self):
        return color(self.type, 'red')
