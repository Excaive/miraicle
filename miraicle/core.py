import requests
import threading
from io import BytesIO

from .message import *
from .display import start_log, end_log, color


class Mirai:
    receiver_funcs = {}
    filter_funcs = {}

    def __init__(self, qq, auth_key, port, session_key=None):
        self.qq = qq
        self.auth_key = auth_key
        self.base_url = f'http://localhost:{port}'
        self.session_key = session_key
        from .filters import BaseFilter, GroupSwitchFilter

        self.__filters: List[Union[BaseFilter, GroupSwitchFilter]] = []
        self.lock = threading.Lock()

    def get_version(self):
        response = requests.get(url=f'{self.base_url}/about').json()
        if 'data' in response and 'version' in response['data']:
            return response['data']['version']

    def run(self):
        if not self.session_key:
            auth_response = self.__auth()
            if all(
                    ['code' in auth_response and auth_response['code'] == 0,
                     'session' in auth_response and auth_response['session']]
            ):
                self.session_key = auth_response['session']
                print(f"sessionKey: {auth_response['session']}")
                verify_response = self.__verify()
                if all(
                        ['code' in verify_response and verify_response['code'] == 0,
                         'msg' in verify_response and verify_response['msg']]
                ):
                    pass
            else:
                if 'code' in auth_response and auth_response['code'] == 1:
                    raise ValueError('invalid authKey')
                else:
                    raise ValueError('unknown response')
        self.__main_loop()

    @start_log
    def __main_loop(self):
        while True:
            time.sleep(0.5)
            try:
                msg_json = self.__fetch_msg(10)
                msg_data = msg_json['data']
            except:
                continue
            for msg_origin in msg_data:
                msg_type = msg_origin.get('type', None)
                msg = self.__handle_msg_origin(msg_origin, msg_type)
                print(msg)
                funcs = self.receiver_funcs.get(msg_type, [])
                if funcs:
                    msg_thread = threading.Thread(target=self.run_thread, args=(funcs, msg))
                    msg_thread.start()

    def run_thread(self, funcs, msg):
        for flt in self.__filters:
            funcs = flt.sift(funcs, self, msg)
        for func in funcs:
            func(self, msg)

    @end_log
    def __auth(self):
        """开始认证"""
        response = requests.post(url=f'{self.base_url}/auth',
                                 json={'authKey': self.auth_key}).json()
        return response

    @end_log
    def __verify(self):
        """校验Session"""
        response = requests.post(url=f'{self.base_url}/verify',
                                 json={'sessionKey': self.session_key, 'qq': self.qq}).json()
        return response

    @end_log
    def __release(self):
        """释放Session"""
        response = requests.post(url=f'{self.base_url}/release',
                                 json={'sessionKey': self.session_key, 'qq': self.qq}).json()
        return response

    @staticmethod
    def __handle_msg_origin(msg_origin, msg_type):
        if msg_type in ['GroupMessage', 'FriendMessage', 'TempMessage', 'GroupRecallEvent', 'MemberCardChangeEvent']:
            msg = eval(msg_type)(msg_origin)
        elif msg_type in ['BotOnlineEvent', 'BotReloginEvent']:
            msg = BotOnlineEvent(msg_origin)
        elif msg_type in ['BotOfflineEventActive', 'BotOfflineEventForce', 'BotOfflineEventDropped']:
            msg = BotOfflineEvent(msg_origin)
        else:
            msg = msg_origin
        return msg

    def send_friend_msg(self, qq, msg):
        """发送好友消息"""
        response = requests.post(url=f'{self.base_url}/sendFriendMessage',
                                 json={'sessionKey': self.session_key,
                                       'qq': qq,
                                       'messageChain': self.__handle_friend_msg_chain(msg)})
        return response

    def send_temp_msg(self, group, qq, msg):
        """发送临时会话消息"""
        response = requests.post(url=f'{self.base_url}/sendTempMessage',
                                 json={'sessionKey': self.session_key,
                                       'qq': qq,
                                       'group': group,
                                       'messageChain': self.__handle_friend_msg_chain(msg)})
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
        elif isinstance(msg, (Plain, At, AtAll, Face, Image, FlashImage, Voice, Xml, Json, App)):
            msg_chain.append(msg.to_json())
        print(color(msg_chain, 'blue'))
        return msg_chain

    def send_group_msg(self, group, msg, quote=None):
        """发送群消息"""
        post_json = {'sessionKey': self.session_key,
                     'group': group,
                     'messageChain': self.__handle_group_msg_chain(msg)}
        if quote:
            post_json['quote'] = quote
        response = requests.post(url=f'{self.base_url}/sendGroupMessage',
                                 json=post_json)
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
        elif isinstance(msg, (Plain, At, AtAll, Face, Image, FlashImage, Voice, Xml, Json, App)):
            msg_chain.append(msg.to_json())
        print(color(msg_chain, 'blue'))
        return msg_chain

    def get_friend_list(self):
        """获取好友列表"""
        response = requests.get(url=f'{self.base_url}/friendList',
                                params={'sessionKey': self.session_key}).json()
        return response

    def recall(self, id):
        """撤回消息"""
        response = requests.post(url=f'{self.base_url}/recall',
                                 params={'sessionKey': self.session_key,
                                         'target': id}).json()
        return response

    def get_group_list(self):
        """获取群列表"""
        response = requests.get(url=f'{self.base_url}/groupList',
                                params={'sessionKey': self.session_key}).json()
        return response

    def get_member_list(self, group):
        """获取群成员列表"""
        response = requests.get(url=f'{self.base_url}/memberList',
                                params={'sessionKey': self.session_key,
                                        'target': group}).json()
        return response

    def get_member_info(self, group, qq):
        """获取群员资料"""
        response = requests.get(url=f'{self.base_url}/memberInfo',
                                params={'sessionKey': self.session_key,
                                        'target': group,
                                        'memberId': qq}).json()
        return response

    def __fetch_msg(self, count):
        response = requests.get(url=f'{self.base_url}/fetchMessage',
                                params={'sessionKey': self.session_key,
                                        'count': count}).json()
        return response

    def upload_img(self, img: Image, type='group'):
        """图片文件上传"""
        response = requests.post(url=f'{self.base_url}/uploadImage',
                                 data={'sessionKey': self.session_key,
                                       'type': type},
                                 files={'img': BytesIO(open(img.path, 'rb').read())}).json()
        return response

    def upload_voice(self, voice: Voice, type='group'):
        """语音文件上传"""
        response = requests.post(url=f'{self.base_url}/uploadVoice',
                                 data={'sessionKey': self.session_key,
                                       'type': type},
                                 files={'voice': BytesIO(open(voice.path, 'rb').read())}).json()
        return response

    def upload_file_and_send(self, path, file, type='Group'):
        """文件上传"""
        response = requests.post(url=f'{self.base_url}/uploadFileAndSend',
                                 data={'sessionKey': self.session_key,
                                       'type': type,
                                       'target': 794843381,
                                       'path': path},
                                 files={'file': BytesIO(open(file, 'rb').read())})
        return response.json()

    def mute(self, group, qq, time):
        """禁言群成员"""
        response = requests.post(url=f'{self.base_url}/mute',
                                 params={'sessionKey': self.session_key,
                                         'target': group,
                                         'memberId': qq,
                                         'time': time}).json()
        return response

    def unmute(self, group, qq):
        """解除群成员禁言"""
        response = requests.post(url=f'{self.base_url}/unmute',
                                 params={'sessionKey': self.session_key,
                                         'target': group,
                                         'memberId': qq}).json()
        return response

    def kick(self, group, qq, msg=''):
        """移除群成员"""
        response = requests.post(url=f'{self.base_url}/kick',
                                 params={'sessionKey': self.session_key,
                                         'target': group,
                                         'memberId': qq,
                                         'msg': msg}).json()
        return response

    def quit(self, group):
        """退出群聊"""
        response = requests.post(url=f'{self.base_url}/quit',
                                 params={'sessionKey': self.session_key,
                                         'target': group}).json()
        return response

    def mute_all(self, group):
        """全体禁言"""
        response = requests.post(url=f'{self.base_url}/muteAll',
                                 params={'sessionKey': self.session_key,
                                         'target': group}).json()
        return response

    def unmute_all(self, group):
        """解除全体禁言"""
        response = requests.post(url=f'{self.base_url}/unmuteAll',
                                 params={'sessionKey': self.session_key,
                                         'target': group}).json()
        return response

    def group_file_list(self, group, dir=None):
        """获取群文件列表"""
        if dir:
            response = requests.get(url=f'{self.base_url}/groupFileList',
                                    params={'sessionKey': self.session_key,
                                            'target': group,
                                            'dir': dir}).json()
        else:
            response = requests.get(url=f'{self.base_url}/groupFileList',
                                    params={'sessionKey': self.session_key,
                                            'target': group}).json()
        return response

    def group_file_info(self, group, file: Union[File, str]):
        """获取群文件详细信息"""
        if isinstance(file, File):
            response = requests.get(url=f'{self.base_url}/groupFileInfo',
                                    params={'sessionKey': self.session_key,
                                            'target': group,
                                            'id': file.file_id}).json()
        else:
            assert isinstance(file, str)
            response = requests.get(url=f'{self.base_url}/groupFileInfo',
                                    params={'sessionKey': self.session_key,
                                            'target': group,
                                            'id': file}).json()
        return response

    def is_owner(self, qq, group):
        member_list = self.get_member_list(group)
        for member in member_list:
            member_qq = member.get('id', None)
            member_permission = member.get('permission', None)
            if member_qq == qq:
                if member_permission == 'OWNER':
                    return True
                else:
                    return False
        return False

    def is_administrator(self, qq, group):
        member_list = self.get_member_list(group)
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
        self.__filters.append(flt)
