import requests
import websocket
import json
import concurrent.futures
from io import BytesIO
from typing import Dict

from .utils import *
from .message import *
from .schedule import Scheduler
from .threadpool import ThreadPool


class Mirai(metaclass=Singleton):
    receiver_funcs = {}
    filter_funcs = {}
    __filters = []

    def __init__(self,
                 qq: int,
                 verify_key: str,
                 port: int,
                 session_key: Optional[str] = None,
                 adapter: str = 'http'):
        """创建一个 Mirai 对象
        :param qq: 要绑定的 bot 的 qq 号
        :param verify_key: 创建 mirai-http-server 时生成的 key, 在 mirai-api-http 的 setting 文件中手动指定
        :param port: 端口号，在 mirai-api-http 的 setting 文件中手动指定
        :param session_key: 经过校验得到的 session 号，可选
        :param adapter: 连接方式，支持 http 和 ws，默认为 http
        """
        self.qq: int = qq
        self.verify_key: str = verify_key
        self.base_url: str = f'{adapter}://localhost:{port}'
        self.session_key: Optional[str] = session_key
        self.adapter: str = adapter
        self.thread_pool: ThreadPool = ThreadPool()

        self.__session: Optional[Union[requests.session, websocket.WebSocket]] = None
        self.__msg_pool: Dict[str, json] = {}
        self.__scheduler: Scheduler = Scheduler()

    def version(self):
        """获取 mirai-api-http 的版本号"""
        response = requests.get(url=f'{self.base_url}/about').json()
        if 'data' in response and 'version' in response['data']:
            return response['data']['version']

    def get_version(self):
        warnings.warn('get_version 方法已弃用，请使用 version 代替', DeprecationWarning)
        response = requests.get(url=f'{self.base_url}/about').json()
        if 'data' in response and 'version' in response['data']:
            return response['data']['version']

    def run(self):
        """开始运行"""
        if self.adapter == 'http':
            self.__http_run()
        elif self.adapter == 'ws':
            self.__ws_run()

    def __http_run(self):
        """使用 http adapter 运行"""
        self.__session = requests.session()
        if not self.session_key:
            verify_response = self.__http_verify()
            if all(
                    ['code' in verify_response and verify_response['code'] == 0,
                     'session' in verify_response and verify_response['session']]
            ):
                self.session_key = verify_response['session']
                print(f"sessionKey: {verify_response['session']}")
                verify_response = self.__http_bind()
                if all(
                        ['code' in verify_response and verify_response['code'] == 0,
                         'msg' in verify_response and verify_response['msg']]
                ):
                    pass
            else:
                if 'code' in verify_response and verify_response['code'] == 1:
                    raise ValueError('invalid verifyKey')
                else:
                    raise ValueError('unknown response')
        self.__http_main_loop()

    def __ws_run(self):
        """使用 ws adapter 运行"""
        connect_response = self.__ws_connect()
        connect_data = connect_response.get('data', {})
        if all(
                ['code' in connect_data and connect_data['code'] == 0,
                 'session' in connect_data and connect_data['session']]
        ):
            self.session_key = connect_data['session']
            print(f"sessionKey: {connect_data['session']}")
        else:
            if 'code' in connect_data and connect_data['code'] == 1:
                raise ValueError('invalid verifyKey')
            else:
                raise ValueError('unknown response')
        self.__ws_main_loop()

    @end_log
    def __http_verify(self):
        """http 开始认证"""
        response = self.__session.post(url=f'{self.base_url}/verify',
                                       json={'verifyKey': self.verify_key}).json()
        return response

    @end_log
    def __http_bind(self):
        """http 绑定 session"""
        response = self.__session.post(url=f'{self.base_url}/bind',
                                       json={'sessionKey': self.session_key,
                                             'qq': self.qq}).json()
        return response

    @end_log
    def __http_release(self):
        """http 释放 session"""
        response = self.__session.post(url=f'{self.base_url}/release',
                                       json={'sessionKey': self.session_key,
                                             'qq': self.qq}).json()
        return response

    @end_log
    def __ws_connect(self):
        """websocket 创建连接"""
        self.__session = websocket.WebSocket()
        self.__session.connect(f'{self.base_url}/all',
                               header={'verifyKey': self.verify_key,
                                       'qq': str(self.qq)})
        response = json.loads(self.__session.recv())
        return response

    def __ws_send(self, command: str, content: json):
        """websocket 发送数据"""
        while True:
            sync_id = str(random.randint(0, 100_000_000))
            if sync_id not in self.__msg_pool:
                break
        self.__session.send(
            json.dumps({'syncId': sync_id,
                        'command': command,
                        'subCommand': None,
                        'content': content}))
        future = concurrent.futures.Future()
        self.__msg_pool[sync_id] = future
        result = future.result()
        return result

    @start_log
    def __http_main_loop(self):
        """http 主循环"""
        while True:
            time.sleep(0.5)
            self.__scheduler.run(self)
            try:
                msg_json = self.__http_fetch_msg(10)
                msg_data = msg_json['data']
                for msg_origin in msg_data:
                    msg_type = msg_origin.get('type', None)
                    msg = self.__handle_msg_origin(msg_origin, msg_type)
                    print(msg)
                    funcs = self.receiver_funcs.get(msg_type, [])
                    if funcs:
                        self.thread_pool.add_task(target=self.__call_plugins, args=(funcs, msg))
            except:
                continue

    def __http_fetch_msg(self, count):
        """http 接收消息"""
        response = self.__session.get(url=f'{self.base_url}/fetchMessage',
                                      params={'sessionKey': self.session_key,
                                              'count': count}).json()
        return response

    @start_log
    def __ws_main_loop(self):
        """ws 主循环"""
        self.thread_pool.add_task(target=self.__call_schedule_plugins)
        while True:
            try:
                msg_json = json.loads(self.__session.recv())
                if msg_json['syncId'] == '-1':
                    msg_origin = msg_json['data']
                    msg_type = msg_origin['type']
                    msg = self.__handle_msg_origin(msg_origin, msg_type)
                    print(msg)
                    funcs = self.receiver_funcs.get(msg_type, [])
                    if funcs:
                        self.thread_pool.add_task(target=self.__call_plugins, args=(funcs, msg))
                else:
                    response = msg_json['data']
                    sync_id = msg_json['syncId']
                    if sync_id in self.__msg_pool:
                        future: concurrent.futures.Future = self.__msg_pool.pop(sync_id)
                        future.set_result(response)
                    else:
                        print(color('Exception: 没有找到对应的 sync_id', 'violet'))
            except:
                pass

    def __call_plugins(self, funcs, msg):
        for flt in self.__filters:
            funcs = flt.sift(funcs, self, msg)
            flt.call(self, msg)
        for func in funcs:
            func(self, msg)

    def __call_schedule_plugins(self):
        while True:
            self.__scheduler.run(self)
            time.sleep(0.5)

    def __handle_msg_origin(self, msg_origin, msg_type):
        if msg_type in ['GroupMessage', 'FriendMessage', 'TempMessage']:
            msg = eval(msg_type)(msg_origin, self.qq)
        elif msg_type in ['GroupRecallEvent', 'MemberCardChangeEvent']:
            msg = eval(msg_type)(msg_origin)
        elif msg_type in ['BotOnlineEvent', 'BotReloginEvent']:
            msg = BotOnlineEvent(msg_origin)
        elif msg_type in ['BotOfflineEventActive', 'BotOfflineEventForce', 'BotOfflineEventDropped']:
            msg = BotOfflineEvent(msg_origin)
        else:
            msg = msg_origin
        return msg

    def send_friend_msg(self, qq: int, msg):
        """发送好友消息
        :param qq: 发送消息目标好友的 QQ 号
        :param msg: 发送的消息
        :return: mirai-api-http 的响应
        """
        msg_chain = self.__handle_friend_msg_chain(msg)
        content = {'sessionKey': self.session_key,
                   'qq': qq,
                   'messageChain': msg_chain}
        if self.adapter == 'http':
            response = self.__session.post(url=f'{self.base_url}/sendFriendMessage', json=content).json()
        else:
            assert self.adapter == 'ws'
            response = self.__ws_send(command='sendFriendMessage', content=content)
        msg_id = response.get('messageId', 0)
        bot_msg = BotMessage(msg_chain, 'FriendMessage', msg_id, qq)
        print(color(bot_msg, 'blue'))
        return response

    def send_temp_msg(self, group: int, qq: int, msg):
        """发送临时会话消息
        :param group: 临时会话群号
        :param qq: 临时会话对象 QQ 号
        :param msg: 发送的消息
        :return: mirai-api-http 的响应
        """
        msg_chain = self.__handle_friend_msg_chain(msg)
        content = {'sessionKey': self.session_key,
                   'qq': qq,
                   'group': group,
                   'messageChain': msg_chain}
        if self.adapter == 'http':
            response = self.__session.post(url=f'{self.base_url}/sendTempMessage', json=content).json()
        else:
            assert self.adapter == 'ws'
            response = self.__ws_send(command='sendTempMessage', content=content)
        msg_id = response.get('messageId', 0)
        bot_msg = BotMessage(msg_chain, 'TempMessage', msg_id, group)
        print(color(bot_msg, 'blue'))
        return response

    @staticmethod
    def __handle_friend_msg_chain(msg):
        msg_chain = []
        if isinstance(msg, (list, tuple)):
            for ele in msg:
                if isinstance(ele, dict):
                    msg_chain.append(ele)
                else:
                    msg_chain.append(ele.to_json())
        elif isinstance(msg, str):
            msg_chain.append(Plain(msg).to_json())
        elif isinstance(msg, Element):
            msg_chain.append(msg.to_json())
        return msg_chain

    def send_group_msg(self, group: int, msg, quote: Optional[int] = None):
        """发送群消息
        :param group: 发送消息目标群的群号
        :param msg: 发送的消息
        :param quote: 引用一条消息的 messageId 进行回复
        :return: mirai-api-http 的响应
        """
        msg_chain = self.__handle_group_msg_chain(msg)
        content = {'sessionKey': self.session_key,
                   'group': group,
                   'messageChain': msg_chain}
        if quote:
            content['quote'] = quote

        if self.adapter == 'http':
            response = self.__session.post(url=f'{self.base_url}/sendGroupMessage', json=content).json()
        else:
            assert self.adapter == 'ws'
            response = self.__ws_send(command='sendGroupMessage', content=content)
        msg_id = response.get('messageId', 0)
        bot_msg = BotMessage(msg_chain, 'GroupMessage', msg_id, group)
        print(color(bot_msg, 'blue'))
        return response

    @staticmethod
    def __handle_group_msg_chain(msg):
        msg_chain = []
        if isinstance(msg, (list, tuple)):
            for ele in msg:
                if isinstance(ele, dict):
                    msg_chain.append(ele)
                else:
                    msg_chain.append(ele.to_json())
        elif isinstance(msg, GroupMessage):
            if msg.json['messageChain'][0]['type'] == 'Source':
                msg_chain = msg.json['messageChain'][1:]
            else:
                msg_chain = msg.json['messageChain']
        elif isinstance(msg, str):
            msg_chain.append(Plain(msg).to_json())
        elif isinstance(msg, Element):
            msg_chain.append(msg.to_json())
        return msg_chain

    def recall(self, msg_id: int):
        """撤回消息
        :param msg_id: 需要撤回的消息的 messageId
        :return: mirai-api-http 的响应
        """
        content = {'sessionKey': self.session_key,
                   'target': msg_id}
        if self.adapter == 'http':
            response = self.__session.post(url=f'{self.base_url}/recall', json=content).json()
            return response
        elif self.adapter == 'ws':
            response = self.__ws_send(command='recall', content=content)
            return response

    def friend_list(self):
        """获取好友列表"""
        content = {'sessionKey': self.session_key}
        if self.adapter == 'http':
            response = self.__session.get(url=f'{self.base_url}/friendList', params=content).json()
            return response
        elif self.adapter == 'ws':
            response = self.__ws_send(command='friendList', content=content)
            return response

    def get_friend_list(self):
        warnings.warn('get_friend_list 方法已弃用，请使用 friend_list 代替', DeprecationWarning)
        content = {'sessionKey': self.session_key}
        if self.adapter == 'http':
            response = self.__session.get(url=f'{self.base_url}/friendList', params=content).json()
            return response
        elif self.adapter == 'ws':
            response = self.__ws_send(command='friendList', content=content)
            return response

    def group_list(self):
        """获取群列表"""
        content = {'sessionKey': self.session_key}
        if self.adapter == 'http':
            response = self.__session.get(url=f'{self.base_url}/groupList', params=content).json()
            return response
        elif self.adapter == 'ws':
            response = self.__ws_send(command='groupList', content=content)
            return response

    def get_group_list(self):
        warnings.warn('get_group_list 方法已弃用，请使用 group_list 代替', DeprecationWarning)
        content = {'sessionKey': self.session_key}
        if self.adapter == 'http':
            response = self.__session.get(url=f'{self.base_url}/groupList', params=content).json()
            return response
        elif self.adapter == 'ws':
            response = self.__ws_send(command='groupList', content=content)
            return response

    def member_list(self, group: int):
        """获取群成员列表"""
        content = {'sessionKey': self.session_key,
                   'target': group}
        if self.adapter == 'http':
            response = self.__session.get(url=f'{self.base_url}/memberList', params=content).json()
            return response
        elif self.adapter == 'ws':
            response = self.__ws_send(command='memberList', content=content)
            return response

    def get_member_list(self, group: int):
        warnings.warn('get_member_list 方法已弃用，请使用 member_list 代替', DeprecationWarning)
        content = {'sessionKey': self.session_key,
                   'target': group}
        if self.adapter == 'http':
            response = self.__session.get(url=f'{self.base_url}/memberList', params=content).json()
            return response
        elif self.adapter == 'ws':
            response = self.__ws_send(command='memberList', content=content)
            return response

    def bot_profile(self):
        """获取 bot 资料
        :return bot 资料
        """
        content = {'sessionKey': self.session_key}
        if self.adapter == 'http':
            response = self.__session.get(url=f'{self.base_url}/botProfile', params=content).json()
            return response
        elif self.adapter == 'ws':
            response = self.__ws_send(command='botProfile', content=content)
            return response

    def friend_profile(self, qq: int):
        """获取好友资料
        :param qq: 好友 QQ 号
        :return 好友资料
        """
        content = {'sessionKey': self.session_key,
                   'target': qq}
        if self.adapter == 'http':
            response = self.__session.get(url=f'{self.base_url}/friendProfile', params=content).json()
            return response
        elif self.adapter == 'ws':
            response = self.__ws_send(command='friendProfile', content=content)
            return response

    def member_profile(self, group: int, qq: int):
        """获取群员资料
        :param group: 指定群的群号
        :param qq: 群员 QQ 号
        :return: 群员资料
        """
        content = {'sessionKey': self.session_key,
                   'target': group,
                   'memberId': qq}
        if self.adapter == 'http':
            response = self.__session.get(url=f'{self.base_url}/memberProfile', params=content).json()
            return response
        elif self.adapter == 'ws':
            response = self.__ws_send(command='memberProfile', content=content)
            return response

    def session_info(self):
        """获取 session 信息
        :return session 信息
        """
        content = {'sessionKey': self.session_key}
        if self.adapter == 'http':
            response = self.__session.get(url=f'{self.base_url}/sessionInfo', params=content).json()
            return response
        elif self.adapter == 'ws':
            response = self.__ws_send(command='sessionInfo', content=content)
            return response

    def upload_img(self, img: Image, type='group'):
        """图片文件上传，当前仅支持 http
        :param img: 上传的 Image 对象
        :param type: 'friend' 或 'group' 或 'temp'
        :return: 图片的 imageId, url 和 path
        """
        response = self.__session.post(url=f'{self.base_url}/uploadImage',
                                       data={'sessionKey': self.session_key,
                                             'type': type},
                                       files={'img': BytesIO(open(img.path, 'rb').read())}).json()
        return response

    def upload_voice(self, voice: Voice, type='group'):
        """语音文件上传，当前仅支持 http
        :param voice: 上传的 Voice 对象
        :param type: 当前仅支持 'group'
        :return: 语音的 voiceId, url 和 path
        """
        response = self.__session.post(url=f'{self.base_url}/uploadVoice',
                                       data={'sessionKey': self.session_key,
                                             'type': type},
                                       files={'voice': BytesIO(open(voice.path, 'rb').read())}).json()
        return response

    def upload_file_and_send(self, path: str, group: int, file, type='Group'):
        """文件上传，当前仅支持 http
        :param path: 文件上传目录与名字
        :param group: 指定群的群号
        :param file: 文件内容
        :param type: 当前仅支持 "Group"
        """
        response = self.__session.post(url=f'{self.base_url}/uploadFileAndSend',
                                       data={'sessionKey': self.session_key,
                                             'type': type,
                                             'target': group,
                                             'path': path},
                                       files={'file': BytesIO(open(file, 'rb').read())}).json()
        return response

    def delete_friend(self, qq: int):
        """删除好友
        :param qq: 好友 QQ 号
        """
        content = {'sessionKey': self.session_key,
                   'target': qq}
        if self.adapter == 'http':
            response = self.__session.post(url=f'{self.base_url}/deleteFriend', json=content).json()
            return response
        elif self.adapter == 'ws':
            response = self.__ws_send(command='deleteFriend', content=content)
            return response

    def mute(self, group: int, qq: int, time: int):
        """禁言群成员
        :param group: 指定群的群号
        :param qq: 指定群员 QQ 号
        :param time: 禁言时长，单位为秒，最多 30 天
        """
        content = {'sessionKey': self.session_key,
                   'target': group,
                   'memberId': qq,
                   'time': time}
        if self.adapter == 'http':
            response = self.__session.post(url=f'{self.base_url}/mute', json=content).json()
            return response
        elif self.adapter == 'ws':
            response = self.__ws_send(command='mute', content=content)
            return response

    def unmute(self, group: int, qq: int):
        """解除群成员禁言
        :param group: 指定群的群号
        :param qq: 指定群员 QQ 号
        """
        content = {'sessionKey': self.session_key,
                   'target': group,
                   'memberId': qq}
        if self.adapter == 'http':
            response = self.__session.post(url=f'{self.base_url}/unmute', json=content).json()
            return response
        elif self.adapter == 'ws':
            response = self.__ws_send(command='unmute', content=content)
            return response

    def kick(self, group: int, qq: int, msg=''):
        """移除群成员
        :param group: 指定群的群号
        :param qq: 指定群员 QQ 号
        :param msg: 信息
        """
        content = {'sessionKey': self.session_key,
                   'target': group,
                   'memberId': qq,
                   'msg': msg}
        if self.adapter == 'http':
            response = self.__session.post(url=f'{self.base_url}/kick', json=content).json()
            return response
        elif self.adapter == 'ws':
            response = self.__ws_send(command='kick', content=content)
            return response

    def quit(self, group: int):
        """退出群聊
        :param group: 退出的群号
        """
        content = {'sessionKey': self.session_key,
                   'target': group}
        if self.adapter == 'http':
            response = self.__session.post(url=f'{self.base_url}/quit', json=content).json()
            return response
        elif self.adapter == 'ws':
            response = self.__ws_send(command='quit', content=content)
            return response

    def mute_all(self, group: int):
        """全体禁言
        :param group: 指定群的群号
        """
        content = {'sessionKey': self.session_key,
                   'target': group}
        if self.adapter == 'http':
            response = self.__session.post(url=f'{self.base_url}/muteAll', json=content).json()
            return response
        elif self.adapter == 'ws':
            response = self.__ws_send(command='muteAll', content=content)
            return response

    def unmute_all(self, group: int):
        """解除全体禁言
        :param group: 指定群的群号
        """
        content = {'sessionKey': self.session_key,
                   'target': group}
        if self.adapter == 'http':
            response = self.__session.post(url=f'{self.base_url}/unmuteAll', json=content).json()
            return response
        elif self.adapter == 'ws':
            response = self.__ws_send(command='unmuteAll', content=content)
            return response

    def set_essence(self, msg_id: int):
        """设置群精华消息
        :param msg_id: 精华消息的 messageId
        """
        content = {'sessionKey': self.session_key,
                   'target': msg_id}
        if self.adapter == 'http':
            response = self.__session.post(url=f'{self.base_url}/setEssence', json=content).json()
            return response
        elif self.adapter == 'ws':
            response = self.__ws_send(command='setEssence', content=content)
            return response

    def member_admin(self, group: int, qq: int, assign: bool = True):
        """修改群员的管理员权限
        :param group: 指定群的群号
        :param qq: 群员 QQ 号
        :param assign: 是否设置为管理员
        """
        content = {'sessionKey': self.session_key,
                   'target': group,
                   'memberId': qq,
                   'assign': assign}
        if self.adapter == 'http':
            response = self.__session.post(url=f'{self.base_url}/memberAdmin', json=content).json()
            return response
        elif self.adapter == 'ws':
            response = self.__ws_send(command='memberAdmin', content=content)
            return response

    def file_list(self, dir_id: Optional[str] = None, path: Optional[str] = None, group: Optional[int] = None,
                  qq: Optional[int] = None, with_download_info: bool = False):
        """获取文件列表，目前仅支持群文件的操作
        :param dir_id: 文件夹 id，空为根目录
        :param path: 文件夹路径，优先级高于 dir_id；文件夹允许重名，不保证准确，准确定位使用 dir_id
        :param group：群号，可选
        :param qq：好友 QQ 号，可选
        :param with_download_info：是否携带下载信息，额外请求，无必要不要携带
        :return: 文件列表
        """
        content = {'sessionKey': self.session_key,
                   'id': dir_id if dir_id else '',
                   'withDownloadInfo': with_download_info}
        if path:
            content['path'] = path
        if group:
            content['group'] = group
        if qq:
            content['qq'] = qq
        if self.adapter == 'http':
            response = self.__session.get(url=f'{self.base_url}/file/list', params=content).json()
            return response
        elif self.adapter == 'ws':
            response = self.__ws_send('file_list', content=content)
            return response

    def file_info(self, file: Union[File, str], path: Optional[str] = None, group: Optional[int] = None,
                  qq: Optional[int] = None, with_download_info: bool = False):
        """获取文件信息
        :param file: 文件对象或文件唯一 ID
        :param path: 文件夹路径，优先级高于 file；文件夹允许重名，不保证准确，准确定位使用 file
        :param group：群号，可选
        :param qq：好友 QQ 号，可选
        :param with_download_info：是否携带下载信息，额外请求，无必要不要携带
        :return: 文件信息
        """
        content = {'sessionKey': self.session_key,
                   'withDownloadInfo': with_download_info}
        if isinstance(file, File):
            content['id'] = file.file_id
        else:
            content['id'] = file
        if path:
            content['path'] = path
        if group:
            content['group'] = group
        if qq:
            content['qq'] = qq
        if self.adapter == 'http':
            response = self.__session.get(url=f'{self.base_url}/file/info', params=content).json()
            return response
        else:
            response = self.__ws_send('file_info', content=content)
            return response

    def is_owner(self, qq: int, group: int):
        """判断某成员在指定群内是否为群主
        :param qq: 指定群员 QQ 号
        :param group: 指定群的群号
        :return: 成员在指定群内是否为群主
        """
        member_list = self.member_list(group)['data']
        if qq == self.qq:
            return member_list[0].get('group', {}).get('permission', None) == 'OWNER'
        for member in member_list:
            member_qq = member.get('id', None)
            member_permission = member.get('permission', None)
            if member_qq == qq:
                if member_permission == 'OWNER':
                    return True
                else:
                    return False
        return False

    def is_administrator(self, qq: int, group: int):
        """判断某成员在指定群内是否为管理员
        :param qq: 指定群员 QQ 号
        :param group: 指定群的群号
        :return: 成员在指定群内是否为管理员
        """
        member_list = self.member_list(group)['data']
        if qq == self.qq:
            return member_list[0].get('group', {}).get('permission', None) in ['OWNER', 'ADMINISTRATOR']
        for member in member_list:
            member_qq = member.get('id', None)
            member_permission = member.get('permission', None)
            if member_qq == qq:
                if member_permission in ['OWNER', 'ADMINISTRATOR']:
                    return True
                else:
                    return False
        return False

    @classmethod
    def receiver(cls, msg_type):
        def wrapper(func):
            if msg_type not in cls.receiver_funcs:
                cls.receiver_funcs[msg_type] = [func]
            else:
                cls.receiver_funcs[msg_type].append(func)
            return func

        return wrapper

    @classmethod
    def filter(cls, filter_type):
        def wrapper(func):
            if filter_type not in cls.filter_funcs:
                cls.filter_funcs[filter_type] = [func]
            else:
                cls.filter_funcs[filter_type].append(func)
            return func

        return wrapper

    @end_log
    def set_filter(self, flt):
        """设置过滤器
        :param flt: 要设置的过滤器"""
        self.__filters.append(flt)
