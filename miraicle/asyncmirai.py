import aiohttp
import asyncio
import json
from io import BytesIO
from typing import Dict

from .utils import *
from .message import *
from .schedule import Scheduler


class AsyncMirai(metaclass=Singleton):
    receiver_funcs = {}
    filter_funcs = {}
    __filters = []

    def __init__(self,
                 qq: int,
                 verify_key: str,
                 port: int,
                 session_key: Optional[str] = None,
                 adapter: str = 'http'):
        """创建一个 AsyncMirai 对象
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

        self.__loop: Optional[asyncio.AbstractEventLoop] = None
        self.__session: Optional[Union[aiohttp.ClientSession, aiohttp.ClientWebSocketResponse]] = None
        self.__msg_pool: Dict[str, json] = {}
        self.__scheduler: Scheduler = Scheduler()

    async def version(self):
        """获取 mirai-api-http 的版本号"""
        async with aiohttp.ClientSession().get(url=f'{self.base_url}/about') as r:
            response = await r.json()
        if 'data' in response and 'version' in response['data']:
            return response['data']['version']

    async def get_version(self):
        warnings.warn('get_version 方法已弃用，请使用 version 代替', DeprecationWarning)
        async with aiohttp.ClientSession().get(url=f'{self.base_url}/about') as r:
            response = await r.json()
        if 'data' in response and 'version' in response['data']:
            return response['data']['version']

    def run(self):
        """开始运行"""
        if self.adapter == 'http':
            self.__loop = asyncio.get_event_loop()
            self.__loop.run_until_complete(self.__http_run())
        elif self.adapter == 'ws':
            self.__loop = asyncio.get_event_loop()
            self.__loop.run_until_complete(self.__ws_run())

    async def __http_run(self):
        """使用 http adapter 运行"""
        self.__session = aiohttp.ClientSession()
        if not self.session_key:
            verify_response = await self.__http_verify()
            if all(
                    ['code' in verify_response and verify_response['code'] == 0,
                     'session' in verify_response and verify_response['session']]
            ):
                self.session_key = verify_response['session']
                print(f"sessionKey: {verify_response['session']}")
                verify_response = await self.__http_bind()
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
        await self.__http_main_loop()

    async def __ws_run(self):
        """使用 ws adapter 运行"""
        async with aiohttp.ClientSession().ws_connect(f'{self.base_url}/all',
                                                      headers={'verifyKey': self.verify_key,
                                                               'qq': str(self.qq)}) as ws:
            self.__session = ws
            connect_response = await ws.receive()
            connect_data = (json.loads(connect_response.data).get('data', {}))
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
            await self.__ws_main_loop()

    @end_log
    async def __http_verify(self):
        """http 开始认证"""
        async with self.__session.post(url=f'{self.base_url}/verify',
                                       json={'verifyKey': self.verify_key}) as r:
            response = await r.json()
        return response

    @end_log
    async def __http_bind(self):
        """http 绑定 session"""
        async with self.__session.post(url=f'{self.base_url}/bind',
                                       json={'sessionKey': self.session_key,
                                             'qq': self.qq}) as r:
            response = await r.json()
        return response

    @end_log
    async def __http_release(self):
        """http 释放 session"""
        async with self.__session.post(url=f'{self.base_url}/release',
                                       json={'sessionKey': self.session_key,
                                             'qq': self.qq}) as r:
            response = await r.json()
        return response

    async def __ws_send(self, command: str, subcommand: str = None, content: json = None):
        """websocket 发送数据"""
        sync_id = str(random.randint(0, 100_000_000))
        await self.__session.send_str(
            json.dumps({'syncId': sync_id,
                        'command': command,
                        'subCommand': subcommand,
                        'content': content}))
        future = self.__loop.create_future()
        self.__msg_pool[sync_id] = future
        result = await future
        return result

    @start_log
    async def __http_main_loop(self):
        """http 主循环"""
        while True:
            await asyncio.sleep(0.5)
            await self.__scheduler.async_run(self)
            try:
                msg_json = await self.__http_fetch_msg(10)
                msg_data = msg_json['data']
                for msg_origin in msg_data:
                    msg_type = msg_origin.get('type', None)
                    msg = self.__handle_msg_origin(msg_origin, msg_type)
                    print(msg)
                    funcs = self.receiver_funcs.get(msg_type, [])
                    if funcs:
                        await self.__call_plugins(funcs, msg)
            except:
                continue

    async def __http_fetch_msg(self, count):
        """http 接收消息"""
        async with self.__session.get(url=f'{self.base_url}/fetchMessage',
                                      params={'sessionKey': self.session_key,
                                              'count': count}) as r:
            response = await r.json()
        return response

    @start_log
    async def __ws_main_loop(self):
        """ws 主循环"""
        self.__loop.create_task(self.__call_schedule_plugins())
        while True:
            response = await self.__session.receive()
            try:
                msg_json = json.loads(response.data)
                if msg_json['syncId'] == '-1':
                    msg_origin = msg_json['data']
                    msg_type = msg_origin['type']
                    msg = self.__handle_msg_origin(msg_origin, msg_type)
                    print(msg)
                    funcs = self.receiver_funcs.get(msg_type, [])
                    if funcs:
                        await self.__call_plugins(funcs, msg)
                else:
                    response = msg_json['data']
                    sync_id = msg_json['syncId']
                    if sync_id in self.__msg_pool:
                        future: asyncio.Future = self.__msg_pool.pop(sync_id)
                        future.set_result(response)
                    else:
                        print(color('Exception: 没有找到对应的 sync_id', 'violet'))
            except:
                pass

    async def __call_plugins(self, funcs, msg):
        for flt in self.__filters:
            funcs = flt.sift(funcs, self, msg)
        tasks = [flt.async_call(self, msg) for flt in self.__filters] + \
                [func(self, msg) for func in funcs]
        for task in tasks:
            self.__loop.create_task(task)

    async def __call_schedule_plugins(self):
        while True:
            await asyncio.sleep(0.5)
            await self.__scheduler.async_run(self)

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

    async def send_friend_msg(self, qq: int, msg):
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
            async with self.__session.post(url=f'{self.base_url}/sendFriendMessage', json=content) as r:
                response = await r.json()
        else:
            assert self.adapter == 'ws'
            response = await self.__ws_send(command='sendFriendMessage', content=content)
        msg_id = response.get('messageId', 0)
        bot_msg = BotMessage(msg_chain, 'FriendMessage', msg_id, qq)
        print(color(bot_msg, 'blue'))
        return response

    async def send_temp_msg(self, group: int, qq: int, msg):
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
            async with self.__session.post(url=f'{self.base_url}/sendTempMessage', json=content) as r:
                response = await r.json()
        else:
            assert self.adapter == 'ws'
            response = await self.__ws_send(command='sendTempMessage', content=content)
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

    async def send_group_msg(self, group: int, msg, quote: Optional[int] = None):
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
            async with self.__session.post(url=f'{self.base_url}/sendGroupMessage', json=content) as r:
                response = await r.json()
        else:
            assert self.adapter == 'ws'
            response = await self.__ws_send(command='sendGroupMessage', content=content)
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

    async def recall(self, msg_id: int):
        """撤回消息
        :param msg_id: 需要撤回的消息的 messageId
        :return: mirai-api-http 的响应
        """
        content = {'sessionKey': self.session_key,
                   'target': msg_id}
        if self.adapter == 'http':
            async with self.__session.post(url=f'{self.base_url}/recall', json=content) as r:
                response = await r.json()
            return response
        elif self.adapter == 'ws':
            response = await self.__ws_send(command='recall', content=content)
            return response

    async def friend_list(self):
        """获取好友列表"""
        content = {'sessionKey': self.session_key}
        if self.adapter == 'http':
            async with self.__session.get(url=f'{self.base_url}/friendList', params=content) as r:
                response = await r.json()
            return response
        elif self.adapter == 'ws':
            response = await self.__ws_send(command='friendList', content=content)
            return response

    async def get_friend_list(self):
        warnings.warn('get_friend_list 方法已弃用，请使用 friend_list 代替', DeprecationWarning)
        content = {'sessionKey': self.session_key}
        if self.adapter == 'http':
            async with self.__session.get(url=f'{self.base_url}/friendList', params=content) as r:
                response = await r.json()
            return response
        elif self.adapter == 'ws':
            response = await self.__ws_send(command='friendList', content=content)
            return response

    async def group_list(self):
        """获取群列表"""
        content = {'sessionKey': self.session_key}
        if self.adapter == 'http':
            async with self.__session.get(url=f'{self.base_url}/groupList', params=content) as r:
                response = await r.json()
            return response
        elif self.adapter == 'ws':
            response = await self.__ws_send(command='groupList', content=content)
            return response

    async def get_group_list(self):
        warnings.warn('get_group_list 方法已弃用，请使用 group_list 代替', DeprecationWarning)
        content = {'sessionKey': self.session_key}
        if self.adapter == 'http':
            async with self.__session.get(url=f'{self.base_url}/groupList', params=content) as r:
                response = await r.json()
            return response
        elif self.adapter == 'ws':
            response = await self.__ws_send(command='groupList', content=content)
            return response

    async def member_list(self, group):
        """获取群成员列表"""
        content = {'sessionKey': self.session_key,
                   'target': group}
        if self.adapter == 'http':
            async with self.__session.get(url=f'{self.base_url}/memberList', params=content) as r:
                response = await r.json()
            return response
        elif self.adapter == 'ws':
            response = await self.__ws_send(command='memberList', content=content)
            return response

    async def get_member_list(self, group):
        warnings.warn('get_member_list 方法已弃用，请使用 member_list 代替', DeprecationWarning)
        content = {'sessionKey': self.session_key,
                   'target': group}
        if self.adapter == 'http':
            async with self.__session.get(url=f'{self.base_url}/memberList', params=content) as r:
                response = await r.json()
            return response
        elif self.adapter == 'ws':
            response = await self.__ws_send(command='memberList', content=content)
            return response

    async def bot_profile(self):
        """获取 bot 资料
        :return bot 资料
        """
        content = {'sessionKey': self.session_key}
        if self.adapter == 'http':
            async with self.__session.get(url=f'{self.base_url}/botProfile', params=content) as r:
                response = await r.json()
            return response
        elif self.adapter == 'ws':
            response = await self.__ws_send(command='botProfile', content=content)
            return response

    async def friend_profile(self, qq):
        """获取好友资料
        :param qq: 好友 QQ 号
        :return 好友资料
        """
        content = {'sessionKey': self.session_key,
                   'target': qq}
        if self.adapter == 'http':
            async with self.__session.get(url=f'{self.base_url}/friendProfile', params=content) as r:
                response = await r.json()
            return response
        elif self.adapter == 'ws':
            response = await self.__ws_send(command='friendProfile', content=content)
            return response

    async def member_profile(self, group: int, qq: int):
        """获取群员资料
        :param group: 指定群的群号
        :param qq: 群员 QQ 号
        :return: 群员资料
        """
        content = {'sessionKey': self.session_key,
                   'target': group,
                   'memberId': qq}
        if self.adapter == 'http':
            async with self.__session.get(url=f'{self.base_url}/memberProfile', params=content) as r:
                response = await r.json()
            return response
        elif self.adapter == 'ws':
            response = await self.__ws_send(command='memberProfile', content=content)
            return response

    async def session_info(self):
        """获取 session 信息
        :return session 信息
        """
        content = {'sessionKey': self.session_key}
        if self.adapter == 'http':
            async with self.__session.get(url=f'{self.base_url}/sessionInfo', params=content) as r:
                response = await r.json()
            return response
        elif self.adapter == 'ws':
            response = await self.__ws_send(command='sessionInfo', content=content)
            return response

    async def upload_img(self, img: Image, type='group'):
        """图片文件上传，当前仅支持 http
        :param img: 上传的 Image 对象
        :param type: 'friend' 或 'group' 或 'temp'
        :return: 图片的 imageId, url 和 path
        """
        async with self.__session.post(url=f'{self.base_url}/uploadImage',
                                       data={'sessionKey': self.session_key,
                                             'type': type},
                                       files={'img': BytesIO(open(img.path, 'rb').read())}) as r:
            response = await r.json()
        return response

    async def upload_voice(self, voice: Voice, type='group'):
        """语音文件上传，当前仅支持 http
        :param voice: 上传的 Voice 对象
        :param type: 当前仅支持 'group'
        :return: 语音的 voiceId, url 和 path
        """
        async with self.__session.post(url=f'{self.base_url}/uploadVoice',
                                       data={'sessionKey': self.session_key,
                                             'type': type},
                                       files={'voice': BytesIO(open(voice.path, 'rb').read())}) as r:
            response = await r.json()
        return response

    async def upload_file_and_send(self, path: str, group: int, file, type='Group'):
        """文件上传，当前仅支持 http
        :param path: 文件上传目录与名字
        :param group: 指定群的群号
        :param file: 文件内容
        :param type: 当前仅支持 "Group"
        """
        async with self.__session.post(url=f'{self.base_url}/uploadFileAndSend',
                                       data={'sessionKey': self.session_key,
                                             'type': type,
                                             'target': group,
                                             'path': path},
                                       files={'file': BytesIO(open(file, 'rb').read())}) as r:
            response = await r.json()
        return response

    async def delete_friend(self, qq: int):
        """删除好友
        :param qq: 好友 QQ 号
        """
        content = {'sessionKey': self.session_key,
                   'target': qq}
        if self.adapter == 'http':
            async with self.__session.post(url=f'{self.base_url}/deleteFriend', json=content) as r:
                response = await r.json()
            return response
        elif self.adapter == 'ws':
            response = await self.__ws_send(command='deleteFriend', content=content)
            return response

    async def mute(self, group: int, qq: int, time: int):
        """禁言群成员
        :param group: 指定群的群号
        :param qq: 指定群员 QQ 号
        :param time: 禁言时长，单位为秒，最多30天
        """
        content = {'sessionKey': self.session_key,
                   'target': group,
                   'memberId': qq,
                   'time': time}
        if self.adapter == 'http':
            async with self.__session.post(url=f'{self.base_url}/mute', json=content) as r:
                response = await r.json()
            return response
        elif self.adapter == 'ws':
            response = await self.__ws_send(command='mute', content=content)
            return response

    async def unmute(self, group: int, qq: int):
        """解除群成员禁言
        :param group: 指定群的群号
        :param qq: 指定群员 QQ 号
        """
        content = {'sessionKey': self.session_key,
                   'target': group,
                   'memberId': qq}
        if self.adapter == 'http':
            async with self.__session.post(url=f'{self.base_url}/unmute', json=content) as r:
                response = await r.json()
            return response
        elif self.adapter == 'ws':
            response = await self.__ws_send(command='unmute', content=content)
            return response

    async def kick(self, group: int, qq: int, msg=''):
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
            async with self.__session.post(url=f'{self.base_url}/kick', json=content) as r:
                response = await r.json()
            return response
        elif self.adapter == 'ws':
            response = await self.__ws_send(command='kick', content=content)
            return response

    async def quit(self, group: int):
        """退出群聊
        :param group: 退出的群号
        """
        content = {'sessionKey': self.session_key,
                   'target': group}
        if self.adapter == 'http':
            async with self.__session.post(url=f'{self.base_url}/quit', json=content) as r:
                response = await r.json()
            return response
        elif self.adapter == 'ws':
            response = await self.__ws_send(command='quit', content=content)
            return response

    async def mute_all(self, group: int):
        """全体禁言
        :param group: 指定群的群号
        """
        content = {'sessionKey': self.session_key,
                   'target': group}
        if self.adapter == 'http':
            async with self.__session.post(url=f'{self.base_url}/muteAll', json=content) as r:
                response = await r.json()
            return response
        elif self.adapter == 'ws':
            response = await self.__ws_send(command='muteAll', content=content)
            return response

    async def unmute_all(self, group: int):
        """解除全体禁言
        :param group: 指定群的群号
        """
        content = {'sessionKey': self.session_key,
                   'target': group}
        if self.adapter == 'http':
            async with self.__session.post(url=f'{self.base_url}/unmuteAll', json=content) as r:
                response = await r.json()
            return response
        elif self.adapter == 'ws':
            response = await self.__ws_send(command='unmuteAll', content=content)
            return response

    async def set_essence(self, msg_id: int):
        """设置群精华消息
        :param msg_id: 精华消息的 messageId
        """
        content = {'sessionKey': self.session_key,
                   'target': msg_id}
        if self.adapter == 'http':
            async with self.__session.post(url=f'{self.base_url}/setEssence', json=content) as r:
                response = await r.json()
            return response
        elif self.adapter == 'ws':
            response = await self.__ws_send(command='setEssence', content=content)
            return response

    async def member_admin(self, group: int, qq: int, assign: bool = True):
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
            async with self.__session.post(url=f'{self.base_url}/memberAdmin', json=content) as r:
                response = await r.json()
            return response
        elif self.adapter == 'ws':
            response = await self.__ws_send(command='memberAdmin', content=content)
            return response

    async def file_list(self, dir_id: Optional[str] = None, group: Optional[int] = None,
                        qq: Optional[int] = None, with_download_info: bool = False):
        """获取文件列表，目前仅支持群文件的操作
        :param dir_id: 文件夹 id，空为根目录
        :param group：群号，可选
        :param qq：好友 QQ 号，可选
        :param with_download_info：是否携带下载信息，额外请求，无必要不要携带
        :return: 文件列表
        """
        content = {'sessionKey': self.session_key,
                   'id': dir_id if dir_id else '',
                   'withDownloadInfo': with_download_info}
        if group:
            content['group'] = group
        if qq:
            content['qq'] = qq
        if self.adapter == 'http':
            async with self.__session.get(url=f'{self.base_url}/file/list', params=content) as r:
                response = await r.json()
            return response
        elif self.adapter == 'ws':
            response = await self.__ws_send('file_list', content=content)
            return response

    async def file_info(self, file: Union[File, str], group: Optional[int] = None,
                        qq: Optional[int] = None, with_download_info: bool = False):
        """获取文件信息
        :param file: 文件对象或文件唯一 ID
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
        if group:
            content['group'] = group
        if qq:
            content['qq'] = qq
        if self.adapter == 'http':
            async with self.__session.get(url=f'{self.base_url}/file/info', params=content) as r:
                response = await r.json()
            return response
        else:
            response = await self.__ws_send('file_info', content=content)
            return response

    async def is_owner(self, qq: int, group: int):
        """判断某成员在指定群内是否为群主
        :param qq: 指定群员 QQ 号
        :param group: 指定群的群号
        :return: 成员在指定群内是否为群主
        """
        member_list = (await self.member_list(group))['data']
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

    async def is_administrator(self, qq: int, group: int):
        """判断某成员在指定群内是否为管理员
        :param qq: 指定群员 QQ 号
        :param group: 指定群的群号
        :return: 成员在指定群内是否为管理员
        """
        member_list = (await self.member_list(group))['data']
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
