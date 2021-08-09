import json
import os
import threading

from .message import *
from .utils import end_log
from .mirai import Mirai
from .asyncmirai import AsyncMirai


class BaseFilter(ABC):
    """过滤器基类，不可实例化"""

    def __init__(self, config_file=None):
        self.config_file = config_file
        self.config = {}
        if config_file:
            self._load_config()

    @abstractmethod
    def sift(self, funcs, bot: Union[Mirai, AsyncMirai], msg):
        """过滤操作，返回 funcs 的一个子列表，这些函数将对 msg 进行处理；
        子类需实现该方法"""

    def call(self, bot: Union[Mirai, AsyncMirai], msg):
        if isinstance(msg, GroupMessage):
            funcs_group_filter = bot.filter_funcs.get(self.__class__.__name__, [])
            for func in funcs_group_filter:
                func(bot, msg, self)

    async def async_call(self, bot: Union[Mirai, AsyncMirai], msg):
        if isinstance(msg, GroupMessage):
            funcs_group_filter = bot.filter_funcs.get(self.__class__.__name__, [])
            for func in funcs_group_filter:
                await func(bot, msg, self)

    @end_log
    def _load_config(self):
        if not os.path.exists(self.config_file):
            self._save_config()
        with open(self.config_file, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

    @end_log
    def _save_config(self):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)


class GroupSwitchFilter(BaseFilter):
    """群组件开关"""

    def __init__(self, config_file):
        super().__init__(config_file)
        self.__funcs = []
        self.__func_names = []
        self.__lock = threading.Lock()

    def sift(self, funcs, bot: Union[Mirai, AsyncMirai], msg):
        if not self.__funcs:
            self.__set_funcs(bot.receiver_funcs)
        if isinstance(msg, (GroupMessage, GroupRecallEvent)):
            funcs_o = []
            group = str(msg.group)
            for func in funcs:
                if group not in self.config:
                    self.config[group] = []
                if func.__name__ in self.config[group]:
                    funcs_o.append(func)
            return funcs_o
        return funcs

    def __set_funcs(self, event):
        group_message_funcs = event.get('GroupMessage', [])
        group_recall_event_funcs = event.get('GroupRecallEvent', [])
        self.__funcs = group_message_funcs + group_recall_event_funcs
        self.__func_names = [func.__name__ for func in self.__funcs]

    def enable(self, group, func_name):
        """在群组 group 启用名为 func_name 的组件"""
        if func_name in self.__func_names:
            with self.__lock:
                self.config[str(group)].append(func_name)
                self._save_config()
            return True
        else:
            return False

    def disable(self, group, func_name):
        """在群组 group 禁用名为 func_name 的组件"""
        if func_name in self.__func_names:
            with self.__lock:
                if func_name in self.config[str(group)]:
                    self.config[str(group)].remove(func_name)
                self._save_config()
            return True
        else:
            return False

    def enable_all(self, group):
        """在群组 group 启用所有组件"""
        with self.__lock:
            self.config[str(group)] = self.__func_names
            self._save_config()
        return True

    def disable_all(self, group):
        """在群组 group 禁用所有组件"""
        with self.__lock:
            self.config[str(group)].clear()
            self._save_config()
        return True

    def funcs_info(self, group=None):
        """显示所有组件信息"""
        if group:
            return [{'func': func.__name__,
                     'help': func.__doc__,
                     'enabled': func.__name__ in self.config[str(group)]}
                    for func in self.__funcs]
        else:
            return [{'func': func.__name__,
                     'help': func.__doc__}
                    for func in self.__funcs]


class BlacklistFilter(BaseFilter):
    """黑名单"""

    def __init__(self, config_file):
        super().__init__(config_file)
        if 'blacklist' not in self.config:
            self.config['blacklist'] = []
            self._save_config()
        self.__lock = threading.Lock()

    def sift(self, funcs, bot: Union[Mirai, AsyncMirai], msg):
        if isinstance(msg, (GroupMessage, FriendMessage, TempMessage)):
            if str(msg.sender) in self.config['blacklist']:
                return []
        return funcs

    def append(self, qq):
        """向黑名单中添加成员"""
        if qq not in self.config['blacklist']:
            with self.__lock:
                self.config['blacklist'].append(str(qq))
                self._save_config()
            return True
        else:
            return False

    def remove(self, qq):
        """从黑名单中移除成员"""
        if str(qq) in self.config['blacklist']:
            with self.__lock:
                self.config['blacklist'].remove(str(qq))
                self._save_config()
            return True
        else:
            return False

    def clear(self):
        """清空黑名单"""
        with self.__lock:
            self.config['blacklist'].clear()
            self._save_config()
        return True

    def show(self):
        """显示黑名单"""
        return self.config['blacklist'].copy()
